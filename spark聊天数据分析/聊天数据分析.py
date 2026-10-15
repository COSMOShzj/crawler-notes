from pyspark.sql import SparkSession
from pyspark.sql.types import *

SparkSession对象 = SparkSession.builder\
    .appName("test-wlw223")\
    .master("local[*]")\
    .config("hive.metastore.uris","thrift://Hadoopvm1:9083")\
    .config("hive.metastore.warehouse.dir","/user/hive/warehouse")\
    .enableHiveSupport()\
    .getOrCreate()
sc = SparkSession对象.sparkContext


数据类型=StructType().\
    add("msg_time",StringType(),nullable=False).\
    add("sender_name",StringType(),nullable=True).\
    add("sender_account",StringType(),nullable=False).\
    add("sender_sex",StringType(),nullable=False).\
    add("sender_ip",StringType(),nullable=True).\
    add("sender_os",StringType(),nullable=False).\
    add("sender_phenotype",StringType(),nullable=False).\
    add("sender_network",StringType(),nullable=False).\
    add("sender_gps",StringType(),nullable=False).\
    add("receiver_name",StringType(),nullable=False).\
    add("receiver_ip",StringType(),nullable=False).\
    add("receiver_account",StringType(),nullable=False).\
    add("receiver_os",StringType(),nullable=False).\
add("receiver_phenotype",StringType(),nullable=False).\
add("receiver_network",StringType(),nullable=False).\
add("receiver_gps",StringType(),nullable=False).\
add("receiver_sex",StringType(),nullable=False).\
add("msg_type",StringType(),nullable=False).\
add("distance",StringType(),nullable=False).\
add("message",StringType(),nullable=False)

excel=SparkSession对象.read.format("csv")\
    .option("sep", "\t")\
.option("header", False)\
.option("encoding", "utf-8")\
.schema(数据类型)\
.load("hdfs://Hadoopvm1:8020/input/test/*")
# excel.show()

excel.createTempView('tb_msg_source')

#====================================etl清洗====================================================
# SparkSession对象.sql("DROP TABLE IF EXISTS jk223_msg.tb_msg_etl")
#
# SparkSession对象.sql("""
#                 create table jk223_msg.tb_msg_etl as
# select *,
# substr(msg_time,1, 10) as dayinfo, substr(msg_time, 12,2) as hourinfo, --获取天和小时
# split(sender_gps,",")[0] as sender_lng, split(sender_gps,",")[1] as sender_lat --提取经度纬度
# from tb_msg_source
#                    """).show()
#
# SparkSession对象.sql("""
#                select * from jk223_msg.tb_msg_etl
#                    """).show()

#===================================指标1：统计今日消息总量====================================================
# SparkSession对象.sql("DROP TABLE IF EXISTS jk223_msg.tb_rs_total_msg_cnt")
#
# SparkSession对象.sql("""
#                 create table jk223_msg.tb_rs_total_msg_cnt comment "今日消息总量"
#                  as
# select
# dayinfo,
# count(*) as total_msg_cnt
# from jk223_msg.tb_msg_etl
# group by dayinfo
#                    """).show()
#
# SparkSession对象.sql("""
#                select * from jk223_msg.tb_rs_total_msg_cnt
#                    """).show()

#===================================指标2：统计每小时消息量、发送和接收用户数===================================================
# SparkSession对象.sql("DROP TABLE IF EXISTS jk223_msg.tb_rs_hour_msg_cnt")
#
# SparkSession对象.sql("""
#                 create table jk223_msg.tb_rs_hour_msg_cnt comment "每小时消息量趋势"
#                  as
# select
# dayinfo,
# hourinfo,
# count(*) as total_msg_cnt,
# count(distinct sender_account) as sender_usr_cnt,   count(distinct receiver_account) as receiver_usr_cnt
# from jk223_msg.tb_msg_etl
# group by dayinfo,hourinfo
#                    """).show()

# SparkSession对象.sql("""
#                select * from jk223_msg.tb_rs_hour_msg_cnt
#                    """).show()

#===================================指标3：统计今日各地区发送消息总量===================================================
# SparkSession对象.sql("""
#                 create table jk223_msg.tb_rs_loc_cnt comment "今日各地区发送消息总量"
#                  as
# select
# dayinfo,
# sender_gps,
# cast(sender_lng as double) as longitude, cast(sender_lat as double) as latitude,    count(*) as total_msg_cnt
# from jk223_msg.tb_msg_etl
# group by dayinfo,sender_gps,sender_lng,sender_lat
#                    """).show()

#===================================指标4：统计今日发送和接收用户人数===================================================
# SparkSession对象.sql("""
#   create table if not exists jk223_msg.tb_rs_usr_cnt   comment "今日发送消息人数、接受消息人数"
# as
# select
# dayinfo,
# count(distinct sender_account) as sender_usr_cnt,   count(distinct receiver_account) as receiver_usr_cnt
# from jk223_msg.tb_msg_etl
# group by dayinfo
#                    """).show()

#===================================指标5：统计发送消息条数最多的Top10用户===================================================
# SparkSession对象.sql("""
# create table if not exists jk223_msg.tb_rs_susr_top10   comment "发送消息条数最多的Top10用户"
# as
# select
# dayinfo,
# sender_name as username,
# count(*) as sender_msg_cnt
# from jk223_msg.tb_msg_etl
# group by dayinfo,sender_name
# order by sender_msg_cnt desc
# limit 10
#                    """).show()

#===================================指标6：统计接收消息条数最多的Top10用户===================================================
# SparkSession对象.sql("""
# create table if not exists jk223_msg.tb_rs_rusr_top10   comment "接受消息条数最多的Top10用户"
# as
# select
# dayinfo,
# receiver_name as username,
# count(*) as receiver_msg_cnt
# from jk223_msg.tb_msg_etl
# group by dayinfo,receiver_name
# order by receiver_msg_cnt desc
# limit 10
#                    """).show()

#=================================== 指标7：统计发送人的手机型号分布情况===================================================
SparkSession对象.sql("""
create table if not exists jk223_msg.tb_rs_sender_phone  comment "发送人的手机型号分布"
as
select
dayinfo,
sender_phenotype,
count(distinct sender_account) as cnt
from jk223_msg.tb_msg_etl
group by dayinfo,sender_phenotype
                   """).show()

#=================================== 指标8：统计发送人的操作系统分布===================================================
SparkSession对象.sql("""
create table if not exists jk223_msg.tb_rs_sender_os comment "发送人的OS分布"
as
select
dayinfo,
sender_os,
count(distinct sender_account) as cnt
from jk223_msg.tb_msg_etl
group by dayinfo,sender_os
                   """).show()

#
# show tables ;