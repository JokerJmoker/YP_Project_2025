# YP_Project_2025
------------------------------------------
активировать env - source env/bin/activate
------------------------------------------
сбросить таблицу в бд
1 - su postgres
2 - psql 
3 - \c mydb
4 - DROP TABLE name;
5 - \q выйти 
6 - su jokerjmoker 
------------------------------------------
обновить бд
flask db init - один раз
flask db migrate
flask db upgrade

flask db stamp head (id) - зачастую легче установить метку на ревизию миграции 
------------------------------------------
jokerjmoker - 270961Ts
------------------------------------------
Сросить бд (если с migrations проблемы)
DROP database name;
CREATE DATABASE name

GRANT ALL PRIVILEGES ON DATABASE "mydb" to jokerjmoker;

ALTER USER jokerjmoker CREATEDB;

\c mydb

GRANT ALL ON schema public TO jokerjmoker; ! важнейшая строка

------------------------------------------
