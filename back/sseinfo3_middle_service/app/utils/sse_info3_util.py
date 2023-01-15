# coding=utf-8
"""
@FileName：sse_info3_util
@ProjectName：
@CreateTime：2022/4/29 下午12:31
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
import datetime
import decimal
import json
import re
import time
from collections import namedtuple
from copy import deepcopy
from enum import IntEnum, Enum
import requests

from configs.sse_info3_conf import user_info_data, user_info_data_plain, idps_token_url, headers
from configs.sse_info3_conf_output import TypeTIdRelationEnum, schema_name_dict
from initialization.logger_process import logger

FileInfoExtractData = namedtuple("FileInfoExtractData", ["file_info", "extract_data"])


def common_prospectus(element, file_info, obj, have_year):

    file_name = file_info.file_name
    file_uuid, file_type = file_name.split(".")[0], file_name.split(".")[1]

    element_value = element.get("value", "")
    if element_value == "" and element.get("children", "") != "":
        element_value = element['children'][0]['children'][0]['value'][0].get("value", "")

    md5_code = ""
    re_search = re.search(r"\"md5\":\s*\"(.*?)\"", element_value)
    if re_search:
        md5_code = re_search.group(1)

    # Bulletin_ID+'DG'+Model_Type_Code+当前时间TIMESTAMP
    obj["uuid"] = "{}DG{}{}".format(file_uuid, element.get("type_code", ""), str(int(time.time())))
    obj["Bulletin_ID"] = file_uuid
    obj["Schema_Name"] = element.get("schema_name", "")
    obj["Model_Type"] = element.get("type", "")
    obj["Model_Type_Code"] = element.get("type_code", "")
    obj["Source"] = file_info.source
    obj["Com_Name"] = file_info.company_full_name
    obj["Anmt_Date"] = file_info.publish_date
    obj["Create_Time"] = datetime.datetime.strftime(file_info.last_update_time, "%Y-%m-%d")  # %Y-%m-%d %H:%M:%S
    obj["Rep_Type_Code"] = file_info.file_version_code
    obj["Rep_Type"] = file_info.file_version
    obj["Src_Url"] = file_info.file_path
    obj["info_type"] = ""
    obj["title"] = file_info.file_title
    obj["fileUrl"] = file_info.pdf_path
    obj["editor"] = "sseinfo"
    obj["md5Code"] = md5_code
    obj["fileFormat"] = file_type
    obj["plate"] = ""
    obj["market"] = ""
    obj["schemaVersion"] = ""
    obj["schema_update_flag"] = ""

    obj["记录ID"] = get_location_data(file_info.audit_item_id)
    if have_year:
        obj["年度"] = get_location_data(file_info.publish_date)

    # 默认有效，直接写死
    obj["是否有效"] = get_location_data(1)


def common_temporary_announcement(element, file_info, obj, have_year):

    for bulletin_type_element in kafka_bulletin_type_idps_id_map.values():
        if bulletin_type_element.bulletin_type == file_info.bulletin_type:
            info_type = bulletin_type_element.feature_type_id
            break

    obj["公告类别"] = file_info.bulletin_type_desc
    obj["info_type"] = info_type
    obj["公司代码"] = file_info.security_code
    obj["作者"] = "sseinfo"
    obj["公告标题"] = file_info.file_title
    obj["提取日期"] = file_info.file_update_time

    obj["文件ID"] = file_info.file_id
    obj["MD5码"] = file_info.file_id

    obj["文件位置"] = file_info.file_path
    obj["原文网址"] = file_info.file_path

    # 建议用http: // static.sse.com.cn拼接siteDocUrl
    file_path = file_info.file_path[1:] if file_info.file_path.startswith("/") else file_info.file_path
    obj["公告原文链接"] = "http://static.sse.com.cn/%s" % file_path

    # 临时公告公司简称 建议置空
    obj["公司简称"] = ""
    obj["Source"] = "DG"
    obj["公告类别编号"] = "%s" % file_info.bulletin_type_code
    # 临时公告公司全称 建议置空
    obj["公司全称"] = ""  # file_info.company_full_name
    obj["披露日期"] = file_info.publish_date


def get_location_data(data="", location_element=None, locations=None):
    if location_element is None and locations is None:
        return {"chars": data,
                "locations": [{
                    "bboxes": "[]",
                    "page_no": -1,
                    "page_size": "[]"
                }]
                }

    elif location_element is not None:
        return {"chars": data,
                "locations": location_element["locations"]}

    else:
        return {"chars": data,
                "locations": locations}


def get_common_part(element, file_info, have_year=True):
    """
    处理公共部分

    """
    obj = dict()

    common_type = common_type_dict.get(file_info.bulletin_type, common_prospectus)
    common_type(element, file_info, obj, have_year)

    return obj


def get_empty_rule_data(file_info, tag_list, data_list, type_key):
    """
    得到得应类型的空事件组

    """

    for tag in tag_list:

        # 数据中不存在对应的 schema_name 信息
        if schema_name_dict.get(tag)["schema_name"] not in [data["Schema_Name"] for data in data_list]:
            empty_common_part_data = get_common_part({}, file_info)

            # 处理对应的类型
            empty_data_dict = get_empty_rule_data_type_dict(file_info, tag)
            empty_common_part_data.update(empty_data_dict.get(type_key, {}))

            data_list.append(empty_common_part_data)


def get_empty_rule_data_type_dict(file_info, tag):
    empty_data_dict = {
        "type_txt": {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                                         schema_name_dict.get(tag, {}).get("type_code", ""),
                                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(tag, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(tag, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(tag, {}).get("schema_name", ""),
            "原文类型编号": get_location_data(schema_name_dict.get(tag, {}).get("txt_type_code", "")),
            "原文类型":  get_location_data(schema_name_dict.get(tag, {}).get("txt_type", "")),
            "原文内容": get_location_data(),
            "一级标题": get_location_data(),
            "一级标题下正文": get_location_data(),
            "二级标题": get_location_data(),
            "二级标题下正文": get_location_data(),
        },
        "type_graph": {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                                         schema_name_dict.get(tag, {}).get("type_code", ""),
                                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(tag, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(tag, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(tag, {}).get("schema_name", ""),
            "图片类型编号": get_location_data(schema_name_dict.get(tag, {}).get("graph_type_code", "")),
            "图片类型": get_location_data(schema_name_dict.get(tag, {}).get("graph_type", "")),
            "图片内容": get_location_data(),
        },
        "info_issuer_info": {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                                         schema_name_dict.get(tag, {}).get("type_code", ""),
                                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(tag, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(tag, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(tag, {}).get("schema_name", ""),
            "发行人中文名称": get_location_data(),
            "发行人英文名称": get_location_data(),
            "成立日期": get_location_data(),
            "有限公司成立日期": get_location_data(),
            "股份公司成立日期": get_location_data(),
            "注册资本": get_location_data(),
            "法定代表人": get_location_data(),
            "注册地址": get_location_data(),
            "主要生产经营地址": get_location_data(),
            "控股股东": get_location_data(),
            "实际控制人": get_location_data(),
            "行业分类": get_location_data(),
            "在其他场所（申请 ）挂牌或上市的情况": get_location_data(),
            "单位": get_location_data("元"),
            "币种": get_location_data("人民币"),
        },
        "info_issuer_intmd": {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                                         schema_name_dict.get(tag, {}).get("type_code", ""),
                                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(tag, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(tag, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(tag, {}).get("schema_name", ""),
            "保荐人": get_location_data(),
            "主承销商": get_location_data(),
            "发行人律师": get_location_data(),
            "其他承销机构": get_location_data(),
            "审计机构": get_location_data(),
            "评估机构": get_location_data(),
            "保荐人律师": get_location_data(),
            "主承销商律师": get_location_data(),
            "验资复核机构": get_location_data(),
        },
        "info_release_profile": {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                                         schema_name_dict.get(tag, {}).get("type_code", ""),
                                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(tag, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(tag, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(tag, {}).get("schema_name", ""),
            "股票种类": get_location_data(),
            "每股面值": get_location_data(),
            "发行股数上限": get_location_data(),
            "发行股数占发行后总股本的比例": get_location_data(),
            "超额配售上限": get_location_data(),
            "其中：发行新股数量": get_location_data(),
            "其中：发行新股数量占发行后总股本的比例": get_location_data(),
            "股东公开发售股份数量": get_location_data(),
            "股东公开发售股份数量占发行后总股本的比例": get_location_data(),
            "发行后总股本上限": get_location_data(),
            "每股发行价格": get_location_data(),
            "发行人高管、员工拟参与战略配售情况（如有）": get_location_data(),
            "保荐人相关子公司拟参与战略配售情况（如有）": get_location_data(),
            "发行市盈率": get_location_data(),
            "发行前每股收益": get_location_data(),
            "发行后每股收益": get_location_data(),
            "发行前每股净资产": get_location_data(),
            "发行后每股净资产": get_location_data(),
            "发行市净率": get_location_data(),
            "发行方式": get_location_data(),
            "发行对象": get_location_data(),
            "承销方式": get_location_data(),
            "拟公开发售股份的股东名称": get_location_data(),
            "拟公开发售股份的股东持股数量": get_location_data(),
            "发行费用分摊原则": get_location_data(),
            "募集资金总额": get_location_data(),
            "募集资金净额": get_location_data(),
            "募集资金投资项目": get_location_data(),
            "发行费用概算：总计": get_location_data(),
            "发行费用概算：承销费": get_location_data(),
            "发行费用概算：保荐费": get_location_data(),
            "发行费用概算：保荐及承销费": get_location_data(),
            "发行费用概算：审计费": get_location_data(),
            "发行费用概算：审计及验资费": get_location_data(),
            "发行费用概算：评估费": get_location_data(),
            "发行费用概算：律师费": get_location_data(),
            "发行费用概算：信息披露费": get_location_data(),
            "发行费用概算：发行手续费": get_location_data(),
            "发行费用概算：发行股份登记托管费": get_location_data(),
            "发行费用概算：其他费用": get_location_data(),
            "发行费用概算：信息披露及其他费用": get_location_data(),
            "刊登发行公告日期": get_location_data(),
            "开始询价推介日期": get_location_data(),
            "刊登定价公告日期": get_location_data(),
            "申购日期": get_location_data(),
            "缴款日期": get_location_data(),
            "股票上市日期": get_location_data(),
        },
        "if_table": {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                                         schema_name_dict.get(tag, {}).get("type_code", ""),
                                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(tag, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(tag, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(tag, {}).get("schema_name", ""),
            "判断类型编号": get_location_data(schema_name_dict.get(tag, {}).get("if_type_code", "")),
            "判断类型": get_location_data(schema_name_dict.get(tag, {}).get("if_type", "")),
            "判断内容": get_location_data(),
            "判断结果": get_location_data(),
        },

    }

    return empty_data_dict


def get_empty_relation_data(file_info, info_point, data_list):
    """
    得到对应信息点的空事件组

    """

    # 一个信息点一个列表，所以当列表大于0时，说明列表内有数据
    if len(data_list) > 0:
        return

    empty_common_part_data = get_common_part({}, file_info)
    empty_data_dict = {
        TypeTIdRelationEnum.info_point_issue_shr: {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                        schema_name_dict.get(TypeTIdRelationEnum.info_point_issue_shr, {}).get("type_code", ""),
                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(TypeTIdRelationEnum.info_point_issue_shr, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(TypeTIdRelationEnum.info_point_issue_shr, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(TypeTIdRelationEnum.info_point_issue_shr, {}).get("schema_name", ""),
            "股东名称":  get_location_data(),
            "发行前持股数量":  get_location_data(),
            "发行前持股比例":  get_location_data(),
            "发行后持股数量":  get_location_data(),
            "发行后持股比例":  get_location_data(),
            "发行前公司的总股本":  get_location_data(),
            "发行后公司的总股本":  get_location_data(),
            "股本单位":  get_location_data("股"),
            "本次拟发行人民币普通股数量":  get_location_data(),
    },
        TypeTIdRelationEnum.info_point_cstdn_part_time: {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                        schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_part_time, {}).get("type_code", ""),
                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_part_time, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_part_time, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_part_time, {}).get("schema_name", ""),
            "人员姓名": get_location_data(),
            "公司职务": get_location_data(),
            "兼职单位": get_location_data(),
            "兼职职务": get_location_data(),
            "与公司的关联关系": get_location_data(),
        },
        TypeTIdRelationEnum.info_point_cstdn_invest: {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                        schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_invest, {}).get("type_code", ""),
                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_invest, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_invest, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(TypeTIdRelationEnum.info_point_cstdn_invest, {}).get("schema_name", ""),
            "人员姓名": get_location_data(),
            "公司职务": get_location_data(),
            "被投资公司": get_location_data(),
            "持股比例": get_location_data(),
        },
        TypeTIdRelationEnum.info_point_five_cust_sell: {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                        schema_name_dict.get(TypeTIdRelationEnum.info_point_five_cust_sell, {}).get("type_code", ""),
                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(TypeTIdRelationEnum.info_point_five_cust_sell, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(TypeTIdRelationEnum.info_point_five_cust_sell, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(TypeTIdRelationEnum.info_point_five_cust_sell, {}).get("schema_name", ""),
            "序号": get_location_data(),
            "报告期": get_location_data(),
            "业务线名称": get_location_data(),
            "对象公司名称": get_location_data(),
            "客户名称": get_location_data(),
            "销售产品类型": get_location_data(),
            "销售金额": get_location_data(),
            "占营业收入的比例": get_location_data(),
            "单位": get_location_data("元"),
            "币种": get_location_data("人民币"),
        },
        TypeTIdRelationEnum.info_point_fin_fare: {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                        schema_name_dict.get(TypeTIdRelationEnum.info_point_fin_fare, {}).get("type_code", ""),
                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(TypeTIdRelationEnum.info_point_fin_fare, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(TypeTIdRelationEnum.info_point_fin_fare, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(TypeTIdRelationEnum.info_point_fin_fare, {}).get("schema_name", ""),
            "报告期": get_location_data(),
            "项目名称": get_location_data(),
            "项目金额": get_location_data(),
            "项目金额占比": get_location_data(),
            "科目类型编码": get_location_data(),
            "科目类型": get_location_data(),
            "单位": get_location_data("元"),
            "币种": get_location_data("人民币"),

        },
        TypeTIdRelationEnum.info_point_core_prod_ratio: {
            "uuid": "{}DG{}{}".format(file_info.file_name.split(".")[0],
                        schema_name_dict.get(TypeTIdRelationEnum.info_point_core_prod_ratio, {}).get("type_code", ""),
                         str(int(time.time()))),
            "Model_Type_Code": schema_name_dict.get(TypeTIdRelationEnum.info_point_core_prod_ratio, {}).get("type_code", ""),
            "Model_Type": schema_name_dict.get(TypeTIdRelationEnum.info_point_core_prod_ratio, {}).get("type", ""),
            "Schema_Name": schema_name_dict.get(TypeTIdRelationEnum.info_point_core_prod_ratio, {}).get("schema_name", ""),
            "报告期": get_location_data(),
            "项目名称": get_location_data(),
            "项目金额": get_location_data(),
            "核心技术产品收入": get_location_data(),
            "主营业务收入": get_location_data(),
            "核心技术产品收入占主营业务收入比例": get_location_data(),
            "单位": get_location_data("元"),
            "币种": get_location_data("人民币"),
        },

    }
    empty_common_part_data.update(empty_data_dict.get(info_point, {}))

    data_list.append(empty_common_part_data)


def get_metas(element):
    """
    创建一个OrderedDict ，并处理公共部分

    """
    metas = {}

    # Bulletin_ID+'DG'+Model_Type_Code+当前时间TIMESTAMP
    metas["uuid"] = element["uuid"]
    metas["Bulletin_ID"] = element["Bulletin_ID"]
    metas["Schema_Name"] = element["Schema_Name"]
    metas["Model_Type"] = element["Model_Type"]
    metas["Model_Type_Code"] = element["Model_Type_Code"]
    metas["Source"] = element["Source"]
    metas["Com_Name"] = element["Com_Name"]
    metas["Anmt_Date"] = element["Anmt_Date"]
    metas["Create_Time"] = element["Create_Time"]
    metas["Rep_Type_Code"] = element["Rep_Type_Code"]
    metas["Rep_Type"] = element["Rep_Type"]
    metas["Src_Url"] = element["Src_Url"]
    metas["info_type"] = element["info_type"]
    metas["title"] = element["title"]
    metas["fileUrl"] = element["fileUrl"]
    metas["editor"] = element["editor"]
    metas["md5Code"] = element["md5Code"]
    metas["fileFormat"] = element["fileFormat"]
    metas["plate"] = element["plate"]
    metas["market"] = element["market"]
    metas["schemaVersion"] = element["schemaVersion"]
    metas["schema_update_flag"] = element["schema_update_flag"]

    return metas


def move_common_part(element):

        # 过滤公共字段
        del element["uuid"]
        del element["Bulletin_ID"]
        del element["Schema_Name"]
        del element["Model_Type"]
        del element["Model_Type_Code"]
        del element["Source"]
        del element["Com_Name"]
        del element["Anmt_Date"]
        del element["Create_Time"]
        del element["Rep_Type_Code"]
        del element["Rep_Type"]
        del element["Src_Url"]
        del element["info_type"]
        del element["title"]
        del element["fileUrl"]
        del element["editor"]
        del element["md5Code"]
        del element["fileFormat"]
        del element["plate"]
        del element["market"]
        del element["schemaVersion"]
        del element["schema_update_flag"]

        return element


def get_info_location_data(element):

    # 重组 element，
    # 对于存在多个值得element 进行重组，
    # 只处理data 部分，坐标取第一条数据的坐标

    if element['value'][0]["after_treatment"] is None:
        return get_location_data()

    regroup_element_data = "，".join([json.loads(element_value["after_treatment"])["data"]
                                     for element_value in element['value']])

    # # 合并坐标
    # regroup_element_locations = [json.loads(element_value["after_treatment"])["locations"][0]
    #                              for element_value in element['value']]

    regroup_element_after_treatment = {"data": regroup_element_data,
                                       "locations": json.loads(element['value'][0]["after_treatment"])["locations"],
                                       "md5": json.loads(element['value'][0]["after_treatment"])["md5"],
                                       }

    # info_value = json.dumps(regroup_element_after_treatment, ensure_ascii=False)
    #
    # if not info_value:
    #     return get_location_data()
    #
    # info_value = json.loads(info_value)

    return get_location_data(regroup_element_after_treatment["data"], location_element=regroup_element_after_treatment)


def get_push_json_data(data_list):

    push_json_data = []
    for schema_k, schema_obj in schema_name_dict.items():
        record_id = 1  # 记录id
        json_data_list = []
        metas = None

        for json_data in data_list[:]:
            if schema_obj["schema_name"] == json_data['Schema_Name']:
                deepcopy_json_data = deepcopy(json_data)
                data_list.remove(json_data)

                metas = get_metas(deepcopy_json_data)
                json_data_move_common = move_common_part(deepcopy_json_data)
                json_data_move_common['记录ID']['chars'] = record_id
                json_data_list.append(json_data_move_common)
                record_id += 1

        file_json_data_dict = {"metas": metas, "results": {"data": json_data_list}}
        file_json_data = json.dumps(file_json_data_dict, ensure_ascii=False)

        push_json_data.append(file_json_data)

    return push_json_data


def get_idps_token():
    """
    获取idps token

    """
    data = user_info_data
    plain = user_info_data_plain

    result = requests.post(idps_token_url, data=data)

    # 兼容新版本
    if result.status_code != 200:
        result = requests.post(idps_token_url, json=data)

    # 兼容明文
    if result.status_code != 200 and plain:
        result = requests.post(idps_token_url, data=plain)

    if result.status_code != 200 and plain:
        result = requests.post(idps_token_url, json=plain)

    if result.status_code == 200:
        access_token = result.json().get("access_token")
        return "Bearer " + access_token

    raise ValueError("get_idps_token 获取IDPS token 失败")


def get_idps_header(idps_token):
    header = headers
    header["Authorization"] = idps_token
    return header


def process_unit(unit):
    """
    单位处理
    """
    unit_rule = r"[\(（]?([十百千万亿]{0,}(?<!持|售|新)[股美元]{1,})"

    logger.error("unit %s" % unit)
    if not isinstance(unit, str):
        logger.error("unit type %s" % type(unit))
        logger.error("unit %s" % unit)
        raise ValueError("需要str 类型的值")

    re_search = re.search(unit_rule, unit)

    if not re_search or unit.strip() == "-":
        return "", 1

    multiplier = 1
    result_unit = re_search.group(1)[-1]
    re_search = re_search.group(1)[:-1]
    re_search = re_search.replace("美", "")

    unit_dict = {
        "个"  : 1
        , "十": 10
        , "百": 100
        , "千": 1000
        , "万": 10000
        , "亿": 100000000
    }
    for unit in re_search:
        multiplier *= unit_dict[unit]

    return result_unit, multiplier


def process_num(num, multiplier):
    """
    数量处理
    """
    if len(num) == 0 or num.strip() == "-":
        return ""

    if num.strip().count("%") > 0:
        num = num.replace("%", "")

    # 保留有效数字
    re_search = re.search(r"[-\d,\.]+", num)
    if re_search:
        num = re_search.group()

    num_replace = num.replace(",", "")
    precision = len(num_replace.split(".")[1]) if len(num_replace.split(".")) == 2 else 2
    format_string = "%." + str(precision) + "f"

    try:
        return format_string % (decimal.Decimal(num_replace) * multiplier)
    except Exception as e:
        return num_replace


def process_date(date):
        """
        日期处理
        """

        if len(date) == 0:
            return ""

        date_year_rule = r"(\d+\s*)年"
        date_month_rule = r"(\d\d?\s*)月"
        date_day_rule = r"(\d\d?\s*)日"

        date_year = re.search(date_year_rule, date)
        date_month = re.search(date_month_rule, date)
        date_day = re.search(date_day_rule, date)

        if date_day:  # date_day.group(1)
            result_date_day = int(date_day.group(1))
        else:
            result_date_day = ""

        if date_month:  # date_day.group(1)
            result_date_month = int(date_month.group(1))
        else:
            result_date_month = ""

        # 没有年份，直接返回
        if date_year:  # date_day.group(1)
            result_date_year = int(date_year.group(1))
        else:

            if date.count("-") > 0:
                return date.strip()
            else:
                return ""

        if result_date_day != "":
            return "%s-%s-%s" % (result_date_year, result_date_month, result_date_day)

        elif result_date_month != "":
            import calendar
            weekday, month_last_day = calendar.monthrange(result_date_year, result_date_month)
            return "%s-%s-%s" % (result_date_year, result_date_month, month_last_day)

        else:
            result_date_month = 12
            import calendar
            weekday, month_last_day = calendar.monthrange(result_date_year, result_date_month)
            return "%s-%s-%s" % (result_date_year, result_date_month, month_last_day)


class FileCategoryEnum(Enum):
    common_prospectus = "科创板招股书"
    common_temporary_announcement = "业绩说明会"
    common_temporary_1001 = "异常波动"

BulletinType = namedtuple("BulletinType", ["feature_type_id", "doc_type_id", "bulletin_type"])
bulletin_type_223 = BulletinType(feature_type_id="223", doc_type_id="131", bulletin_type="科创板招股书")

kafka_bulletin_type_idps_id_map = {
    "223": BulletinType(feature_type_id="223", doc_type_id="131", bulletin_type="科创板招股书"),

    "2699": BulletinType(feature_type_id="234", doc_type_id="222", bulletin_type="业绩说明会"),
    "3111": BulletinType(feature_type_id="234", doc_type_id="222", bulletin_type="业绩说明会"),
    "3119": BulletinType(feature_type_id="234", doc_type_id="222", bulletin_type="业绩说明会"),

    "1001": BulletinType(feature_type_id="236", doc_type_id="137", bulletin_type="异常波动"),
}

common_type_dict = {
    FileCategoryEnum.common_prospectus.value: common_prospectus,
    FileCategoryEnum.common_temporary_announcement.value: common_temporary_announcement,
    FileCategoryEnum.common_temporary_1001.value: common_temporary_announcement,
}
