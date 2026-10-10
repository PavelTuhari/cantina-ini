-- История cantina.ini в бэк-офисе. Ставится в схему бэк-офиса (ту, куда
-- смотрит DB link фронта, например BONUS2019_07) один раз; фронты пишут
-- сюда через свой линк вызовом cantina_ini.push_history.
--
-- Почему строки, а не CLOB: через DB link нельзя передать LOB как параметр
-- (ORA-22992), а строка до 4000 байт проходит в любой версии Oracle от 10g.
-- Версия = заголовок в CANTINA_INI_HIST + строки файла в CANTINA_INI_HIST_LINES.
-- Пока версия не закрыта end_version, она в статусе OPEN и в отчётах не видна.
--
-- Запуск: sqlplus <back>/...@<tns> @cantina_ini_hist.sql   (или FrontArchive: ini hist-install)

create sequence cantina_ini_ver_seq;

create table cantina_ini_ver (
  hist_id      number        not null,
  schema_name  varchar2(128) not null,     -- схема фронта, откуда пришло
  pos_id       varchar2(40),               -- PosID из файла
  file_name    varchar2(64)  not null,     -- cantina.ini, selftest.ini
  saved_at     date default sysdate not null,
  pushed_from  varchar2(400),              -- кто сохранил: хост:путь (c_source пакета фронта)
  sha256       varchar2(64)  not null,     -- хеш байтов файла, как у cantina_ini.get_hash
  byte_count   number,
  line_count   number        not null,
  status       varchar2(10) default 'OPEN' not null,   -- OPEN -> DONE
  note         varchar2(400),
  constraint cantina_ini_ver_pk primary key (hist_id),
  constraint cantina_ini_ver_st check (status in ('OPEN', 'DONE'))
);
create index cantina_ini_ver_ix on cantina_ini_ver (schema_name, file_name, hist_id);

create table cantina_ini_ver_lines (
  hist_id  number         not null,
  line_no  number         not null,
  line     varchar2(4000),                 -- без CR/LF; пустая строка = null
  constraint cantina_ini_ver_lines_pk primary key (hist_id, line_no),
  constraint cantina_ini_ver_lines_fk foreign key (hist_id)
    references cantina_ini_ver (hist_id) on delete cascade
);

create or replace package cantina_ini_hist as
  -- Вызываются фронтом через DB link, все параметры скалярные.
  -- begin_version: 0, если такая же версия (sha256) уже последняя для схемы и файла.
  function  begin_version(p_schema varchar2, p_pos_id varchar2, p_file varchar2,
                          p_sha256 varchar2, p_bytes number, p_lines number,
                          p_from varchar2) return number;
  procedure add_line(p_hist_id number, p_line_no number, p_line varchar2);
  procedure end_version(p_hist_id number);

  -- Для бэк-офиса.
  function  last_id(p_schema varchar2, p_file varchar2 default 'cantina.ini') return number;
  function  get_file(p_hist_id number) return clob;                       -- текст версии, CRLF
  function  get_value(p_hist_id number, p_key varchar2,
                      p_section varchar2 default 'General') return varchar2;
  function  diff_text(p_old number, p_new number) return clob;            -- "- строка" / "+ строка"
  procedure purge(p_schema varchar2, p_keep number default 50);            -- оставить последние N версий
end cantina_ini_hist;
/

create or replace package body cantina_ini_hist as
  c_nl constant varchar2(2) := chr(13) || chr(10);

  function last_id(p_schema varchar2, p_file varchar2 default 'cantina.ini') return number is
    l_id number;
  begin
    select max(hist_id) into l_id from cantina_ini_ver
     where schema_name = upper(p_schema) and lower(file_name) = lower(p_file) and status = 'DONE';
    return l_id;
  end;

  function begin_version(p_schema varchar2, p_pos_id varchar2, p_file varchar2,
                         p_sha256 varchar2, p_bytes number, p_lines number,
                         p_from varchar2) return number is
    l_last number := last_id(p_schema, p_file);
    l_sha  varchar2(64);
    l_id   number;
  begin
    if l_last is not null then
      select sha256 into l_sha from cantina_ini_ver where hist_id = l_last;
      if l_sha = p_sha256 then
        return 0;                                   -- без изменений
      end if;
    end if;
    -- незакрытые версии той же схемы (оборванный push) - убираем
    delete from cantina_ini_ver
     where schema_name = upper(p_schema) and lower(file_name) = lower(p_file) and status = 'OPEN';
    select cantina_ini_ver_seq.nextval into l_id from dual;
    insert into cantina_ini_ver (hist_id, schema_name, pos_id, file_name, pushed_from,
                                  sha256, byte_count, line_count)
    values (l_id, upper(p_schema), p_pos_id, p_file, substr(p_from, 1, 400),
            p_sha256, p_bytes, p_lines);
    return l_id;
  end;

  procedure add_line(p_hist_id number, p_line_no number, p_line varchar2) is
  begin
    insert into cantina_ini_ver_lines (hist_id, line_no, line)
    values (p_hist_id, p_line_no, substrb(p_line, 1, 4000));
  end;

  procedure end_version(p_hist_id number) is
    l_expected number; l_got number;
  begin
    select line_count into l_expected from cantina_ini_ver where hist_id = p_hist_id and status = 'OPEN';
    select count(*) into l_got from cantina_ini_ver_lines where hist_id = p_hist_id;
    if l_got <> l_expected then
      raise_application_error(-20002, 'cantina_ini_hist: версия ' || p_hist_id || ': строк '
                              || l_got || ' вместо ' || l_expected);
    end if;
    update cantina_ini_ver set status = 'DONE' where hist_id = p_hist_id;
  end;

  function get_file(p_hist_id number) return clob is
    l clob;
  begin
    dbms_lob.createtemporary(l, true, dbms_lob.call);
    for r in (select line from cantina_ini_ver_lines where hist_id = p_hist_id order by line_no) loop
      if r.line is not null then dbms_lob.writeappend(l, length(r.line), r.line); end if;
      dbms_lob.writeappend(l, 2, c_nl);
    end loop;
    return l;
  end;

  function get_value(p_hist_id number, p_key varchar2,
                     p_section varchar2 default 'General') return varchar2 is
    l_section varchar2(200) := '';
    l_line    varchar2(4000);
    l_eq      pls_integer;
  begin
    for r in (select line from cantina_ini_ver_lines where hist_id = p_hist_id order by line_no) loop
      l_line := ltrim(rtrim(r.line));
      if l_line like '[%]' then
        l_section := substr(l_line, 2, length(l_line) - 2);
      elsif l_line is not null and substr(l_line, 1, 1) not in ('#', ';')
            and lower(l_section) = lower(p_section) then
        l_eq := instr(l_line, '=');
        if l_eq > 1 and lower(trim(substr(l_line, 1, l_eq - 1))) = lower(p_key) then
          return trim(substr(l_line, l_eq + 1));   -- первая сверху, как у кассы
        end if;
      end if;
    end loop;
    return null;
  end;

  function diff_text(p_old number, p_new number) return clob is
    l clob;
    procedure add(p varchar2) is begin
      dbms_lob.writeappend(l, length(p) + 2, p || c_nl);
    end;
  begin
    dbms_lob.createtemporary(l, true, dbms_lob.call);
    for r in (select line_no, line from cantina_ini_ver_lines where hist_id = p_old
              and nvl(line, '~') not in (select nvl(line, '~') from cantina_ini_ver_lines where hist_id = p_new)
              order by line_no) loop
      add('- ' || r.line);
    end loop;
    for r in (select line_no, line from cantina_ini_ver_lines where hist_id = p_new
              and nvl(line, '~') not in (select nvl(line, '~') from cantina_ini_ver_lines where hist_id = p_old)
              order by line_no) loop
      add('+ ' || r.line);
    end loop;
    return l;
  end;

  procedure purge(p_schema varchar2, p_keep number default 50) is
  begin
    delete from cantina_ini_ver h
     where schema_name = upper(p_schema)
       and hist_id not in (select hist_id from (select hist_id, row_number() over
                           (partition by file_name order by hist_id desc) rn
                           from cantina_ini_ver where schema_name = upper(p_schema)) where rn <= p_keep);
  end;
end cantina_ini_hist;
/

-- Последняя версия каждого файла каждой схемы: что сейчас стоит на кассах
create or replace view v_cantina_ini_current as
select h.schema_name, h.pos_id, h.file_name, h.hist_id, h.saved_at, h.pushed_from, h.sha256, h.line_count,
       cantina_ini_hist.get_value(h.hist_id, 'Server')        as server,
       cantina_ini_hist.get_value(h.hist_id, 'FiscalPrinter') as fiscal_printer
  from cantina_ini_ver h
 where h.status = 'DONE'
   and h.hist_id = (select max(hist_id) from cantina_ini_ver x
                     where x.schema_name = h.schema_name and x.file_name = h.file_name and x.status = 'DONE');

-- Лента изменений: каждая версия и сколько строк ушло / пришло относительно предыдущей
create or replace view v_cantina_ini_changes as
select h.hist_id, h.schema_name, h.pos_id, h.file_name, h.saved_at, h.pushed_from, h.sha256,
       lag(h.hist_id) over (partition by h.schema_name, h.file_name order by h.hist_id) as prev_id,
       h.line_count - nvl(lag(h.line_count) over (partition by h.schema_name, h.file_name order by h.hist_id), 0) as lines_delta
  from cantina_ini_ver h
 where h.status = 'DONE';
