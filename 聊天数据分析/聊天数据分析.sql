--建库建表

--如果数据库已存在就删除
drop database if exists db_msg cascade ;
--创建数据库
create database db_msg;
--切换数据库
use db_msg;
--列举数据库
show databases;
--建表
create table tb_msg_source(
  msg_time             string  comment "消息发送时间"
  , sender_name        string  comment "发送人昵称"
  , sender_account     string  comment "发送人账号"
  , sender_sex         string  comment "发送人性别"
  , sender_ip          string  comment "发送人ip地址"
  , sender_os          string  comment "发送人操作系统"
  , sender_phonetype   string  comment "发送人手机型号"
  , sender_network     string  comment "发送人网络类型"
  , sender_gps         string  comment "发送人的GPS定位"
  , receiver_name      string  comment "接收人昵称"
  , receiver_ip        string  comment "接收人IP"
  , receiver_account   string  comment "接收人账号"
  , receiver_os        string  comment "接收人操作系统"
  , receiver_phonetype string  comment "接收人手机型号"
  , receiver_network   string  comment "接收人网络类型"
  , receiver_gps       string  comment "接收人的GPS定位"
  , receiver_sex       string  comment "接收人性别"
  , msg_type           string  comment "消息类型"
  , distance           string  comment "双方距离"
  , message            string  comment "消息内容"
)
--指定分隔符为制表符
row format delimited fields terminated by '\t';

--加载到Hive表中

load data inpath '/hivedata/data1.tsv' into table db_msg.tb_msg_source;
load data inpath '/hivedata/data2.tsv' into table db_msg.tb_msg_source;


	  --  验证结果
select
msg_time,sender_name,sender_ip,sender_phonetype,receiver_name,receiver_network from tb_msg_source limit 10;

	   -- 数据问题
--问题1：当前数据中，有一些数据的字段为空，  不是合法数据
select
msg_time,
sender_name,
sender_gps
from db_msg.tb_msg_source where length(sender_gps) = 0 limit 10;

--问题2：需求中，需要统计每天、每个小时的消息量，  但是数据中没有天和小时字段，只有整体时间字段，不好处理
select
msg_time
from db_msg.tb_msg_source limit 10;

--问题3：需求中，需要对经度和维度构建地区的可视化地图，  但是数据中GPS经纬度为一个字段，不好处理
select
sender_gps
from db_msg.tb_msg_source limit 10;

--	    ETL需求

	     --需求1：对字段为空的不合法数据进行过滤

--•      Where过滤

	    -- 需求2：通过时间字段构建天和小时字段

--•      Substr函数

	 --    需求3：从GPS的经纬度中提取经度和维度

--•      Split函数

	     --需求4：将ETL以后的结果保存到一张新的Hive表中


--•      Create table …… as select ……


	   -- ETL实现
--如果表已存在就删除
drop table if exists tb_msg_etl;
--将Select语句的结果保存到新表中
create table tb_msg_etl as
select *,
substr(msg_time,1, 10) as dayinfo, substr(msg_time, 12,2) as hourinfo, --获取天和小时
split(sender_gps,",")[0] as sender_lng, split(sender_gps,",")[1] as sender_lat --提取经度纬度
from tb_msg_source
--过滤字段为空的数据

where length(sender_gps) > 0 ;

	    --查看结果
select
msg_time,dayinfo,hourinfo,sender_gps,sender_lng,sender_lat
from db_msg.tb_msg_etl
limit 10;

select *
from db_msg.tb_msg_etl
limit 10;

select count(msg_time) from tb_msg_source;
select count(msg_time) from tb_msg_etl;
--需求指标统计


	  --  指标1：统计今日消息总量

--保存结果表
create table if not exists tb_rs_total_msg_cnt comment "今日消息总量"
as
select
dayinfo,
count(*) as total_msg_cnt
from tb_msg_etl
group by dayinfo;

select *
from tb_rs_total_msg_cnt;

	 --   指标2：统计每小时消息量、发送和接收用户数

--保存结果表
create table if not exists tb_rs_hour_msg_cnt
comment "每小时消息量趋势"
as
select
dayinfo,
hourinfo,
count(*) as total_msg_cnt,
count(distinct sender_account) as sender_usr_cnt,   count(distinct receiver_account) as receiver_usr_cnt
from tb_msg_etl
group by dayinfo,hourinfo;

select *
from tb_rs_hour_msg_cnt;
	   -- 指标3：统计今日各地区发送消息总量

--保存结果表
create table if not exists tb_rs_loc_cnt      comment "今日各地区发送消息总量"
as
select
dayinfo,
sender_gps,
cast(sender_lng as double) as longitude, cast(sender_lat as double) as latitude,    count(*) as total_msg_cnt
from tb_msg_etl
group by dayinfo,sender_gps,sender_lng,sender_lat;

select *
from tb_rs_loc_cnt;
	  --  指标4：统计今日发送和接收用户人数

--保存结果表
create table if not exists tb_rs_usr_cnt                          comment "今日发送消息人数、接受消息人数"
as
select
dayinfo,
count(distinct sender_account) as sender_usr_cnt,   count(distinct receiver_account) as receiver_usr_cnt
from tb_msg_etl
group by dayinfo;

select *
from tb_rs_usr_cnt;
	   -- 指标5：统计发送消息条数最多的Top10用户

--保存结果表
create table if not exists tb_rs_susr_top10               comment "发送消息条数最多的Top10用户"
as
select
dayinfo,
sender_name as username,
count(*) as sender_msg_cnt
from tb_msg_etl
group by dayinfo,sender_name
order by sender_msg_cnt desc
limit 10;

select *
from tb_rs_susr_top10;
	   -- 指标6：统计接收消息条数最多的Top10用户

--保存结果表
create table if not exists tb_rs_rusr_top10                 comment "接受消息条数最多的Top10用户"
as
select
dayinfo,
receiver_name as username,
count(*) as receiver_msg_cnt
from db_msg.tb_msg_etl
group by dayinfo,receiver_name
order by receiver_msg_cnt desc
limit 10;

select *
from tb_rs_rusr_top10;
	 --   指标7：统计发送人的手机型号分布情况

--保存结果表
create table if not exists tb_rs_sender_phone  comment "发送人的手机型号分布"
as
select
dayinfo,
sender_phonetype,
count(distinct sender_account) as cnt
from tb_msg_etl
group by dayinfo,sender_phonetype;

select *
from tb_rs_sender_phone;
	    --指标8：统计发送人的操作系统分布

--保存结果表
create table if not exists tb_rs_sender_os comment "发送人的OS分布"
as
select
dayinfo,
sender_os,
count(distinct sender_account) as cnt    
from tb_msg_etl
group by dayinfo,sender_os;

select *
from tb_rs_sender_os;

show tables ;
