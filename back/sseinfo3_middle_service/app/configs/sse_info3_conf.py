# coding=utf-8
"""
@FileName：sse_info3_conf
@ProjectName：
@CreateTime：2021/12/10 上午9:30
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

配置文件
"""
from utils.loader import conf_loader
from collections import namedtuple

sse_client_id = "422228cf02d54820bf0af9acd80f4c40"
sse_client_secret = "a2ae01949d3c4777a06f577414916e12"

sse_token_url = "https://passport.sseinfo.com/auth/oauth/token"
sse_token_url_complete = sse_token_url + "?grant_type=client_credentials&scope=sseuser" \
                                         "&client_id={client_id}" \
                                         "&client_secret={client_secret}"\
                                        .format(client_id=sse_client_id, client_secret=sse_client_secret)

sse_query_url = "https://open.sseinfo.com/api/v1/kcbipo/commonSoaQuery.do"
sse_query_url_complete = sse_query_url + "?isPagination=true&sqlId=GP_GPZCZ_SHXXPL&fileType=30" \
                                   "&pageHelp.pageNo={page_no}" \
                                    "&pageHelp.pageSize={page_size}"

sse_down_file_url = "http://static.sse.com.cn/stock"
sse_down_file_url_complete = "http://static.sse.com.cn/stock{file_path}"
nas_down_file_url_complete = "/projects/data/page/cn{file_path}"

file_base_path = "../data/"

# 上证测试环境
idps_base_url = "http://extract-admin-html:8080"
# 内部测试环境
#idps_base_url = "http://extract_admin_html:80"
# # 本地测试
# idps_base_url_pro =  "https://idps2-sseinfo3.datagrand.cn"
# idps_base_url_test = "http://idps2-sseinfo3.test.datagrand.cn"
# idps_url_is_test = True
# idps_base_url = idps_base_url_test if idps_url_is_test else idps_base_url_pro

idps_token_url = idps_base_url + "/api/login?_allow_anonymous=true"

# 创建抽取任务
idps_feature_type_id = conf_loader('IDPS_FEATURE_TYPE_ID', '223')
idps_doc_type_id = conf_loader('IDPS_DOC_TYPE_ID', '131')
idps_extract_url = idps_base_url + "/api/extracting/v2/task?feature_type_id={feature_type_id}&async_task=true".format(feature_type_id=idps_feature_type_id)
idps_extract_sseinfo3_url = idps_base_url + "/api/task_sseinfo3/v2/task_sseinfo3?feature_type_id={feature_type_id}&async_task=true".format(feature_type_id=idps_feature_type_id)
idps_parser_url = idps_base_url + "/api/document_management/document_upload?file_types=1"

headers = {
    'Referer': 'www.sse.com.cn',
    # 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl9pc3N1ZV90aW1lIjoiMjAyMS0xMi0wNiAxNTozMDoyMSIsInNjb3BlIjpbInNzZXVzZXIiXSwiaXNzIjoic3NlaW5mbyIsImV4cCI6MTYzODc4MzAyMSwidG9rZW5fZXhwaXJlX3RpbWUiOiIyMDIxLTEyLTA2IDE3OjMwOjIxIiwiYXV0aG9yaXRpZXMiOlsic3NldXNlciIsImltYWdlIiwidXNlcl9pbmZvIiwiYXV0aCJdLCJqdGkiOiJiMWNhYTUzYy1hYmRlLTRlYzgtYWM3Zi05MjM4OTVjOWYzYmQiLCJjbGllbnRfaWQiOiI0MjIyMjhjZjAyZDU0ODIwYmYwYWY5YWNkODBmNGM0MCJ9.kdFpmqLMPylqSztXk6anl-dAj8f3RcLF9yqb-LZn6CraGmFio9RVfnqwMPZetLmvLvN_Pa89TW-H9ui9q5H7ELgk16rdU2OK9m9ehKlxOjIMTV6iH3UIt0RwI_U-UuBPIEhLBKfW8mry_7SE8tHcKRvtnjhJjICMgt_YjfTCDB3i--mKeEHl3Wct-ZqAGkusZgpyRxWQVvhmAK1VcPQXR0uQLtfdnIlAnsQwJaMbzHna6VnYj_KLGvUvpRR1no7ZpPId5-lTwW5tqLcIyeUDIf_2IlJCocl2a0VTQtMNF31_RxEHHGIcGhcNangP2NLyvjeLPzbfz9V9_c-UOrotsw'
}


user_info_data = {
    "username": "ZG93bmxvYWRmaWxl"
    , "password": "Q3N3NjI5MTczMDEk"
}

user_info_data_plain = {
    "username": "downloadfile"
    , "password": "Csw62917301$"
}

# 一次定时任务，最多处理 down_file_num 个有效文档
down_file_max_num = conf_loader('DOWN_FILE_MAX_NUM', '2')
down_file_max_num_day = conf_loader('DOWN_FILE_MAX_NUM_DAY ', '200')

idps_extract_result_url = idps_base_url+"/api/extracting/v2/{extract_id}"
min_file_update_time = conf_loader("MIN_FILE_UPDATE_TIME", "20211220")

# PushKafkaService
time_unit = conf_loader("TIME_UNIT", "d")  # %Y-%m-%d %H:%M:%S
time_interval = int(conf_loader("TIME_INTERVAL", "10"))  # %Y-%m-%d %H:%M:%S

# 通过 url 或者 kafka 获取文件信息
input_file_by_api = conf_loader('INPUT_FILE_BY_API', "False")
# 通过 url 或者 路径 获取文件
fetch_file_by_nas = conf_loader('FETCH_FILE_BY_NAS', "True")

