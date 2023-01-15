# coding=utf-8
"""
@FileName：push_kafka
@ProjectName：
@CreateTime：2022/2/17 下午3:20
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""

from flask import g

from configs.push_kafka_conf import topic_dict
from configs.sse_info3_conf import idps_extract_result_url
from configs.sse_info3_conf_output import *
from initialization.logger_process import logger_exception
from models.data_input_model import DownFileModel
from models.extract import ExtractModel
from services.push_kafka_temporary_announcement import PushKafkaTemporaryAnnouncementService
from utils.sse_info3_util import *
from utils.table_to_html_tools import gen_html_document


class PushKafkaService(object):

    def __init__(self):
        self.idps_token = get_idps_token()

    def logic(self):

        # 查询要推送的抽取id
        di_down_file_list = PushKafkaService.get_push_extract_id()

        logger.info("开始处理数据")
        # 一篇一篇的处理
        for down_file_obj in di_down_file_list:

            try:
            # 兼容临时公告
                if down_file_obj.bulletin_type == "" or down_file_obj.bulletin_type == FileCategoryEnum.common_prospectus.value:
                    push_json_data_list = self.dispose_prospectus(down_file_obj.extract_id)
                else:
                    push_json_data = PushKafkaTemporaryAnnouncementService(self.idps_token).dispose_temporary_announcement(down_file_obj.extract_id)
                    push_json_data_list = [push_json_data]

            except Exception as e:
                logger_exception()
                continue

            if len(push_json_data_list) == 0:
                continue

            logger.info("push_json_data_list  len %s" % len(push_json_data_list))
            # 推送kafka
            topic = topic_dict.get(down_file_obj.bulletin_type, topic_dict.get(FileCategoryEnum.common_prospectus.value))

            self.push_kafka(push_json_data_list, topic)

            # with open("../data/%s.json" % down_file_obj.file_title, "w") as wf:
            #     wf.write(json.dumps({down_file_obj.extract_id: push_json_data_list}, ensure_ascii=False, indent="\t"))

            # 向下输出成功，更新 extract_last_update_time
            DownFileModel.update_extract_last_update_time(down_file_obj.extract_id)

        return "成功"

    def dispose_prospectus(self, extract_id):

        file_info_rule_extract, file_info_relation_extract = self.get_file_info_and_extract_data(
            extract_id=extract_id)

        # 处理 file_info_rule_extract
        rule_data = self.dispose_file_info_rule_extract(file_info_rule_extract)

        # 处理 file_info_relation_extract
        relation_data = self.dispose_file_info_relation_extract(file_info_relation_extract)

        # 处理成kafka 所需要的格式
        rule_relation_data = rule_data + relation_data
        push_json_data_list = get_push_json_data(rule_relation_data)

        return push_json_data_list

    @staticmethod
    def get_push_extract_id():
        """
        查询要推送的抽取id
        """
        #
        # 特殊处理，g.time_interval*2  多覆盖一些数据
        seconds = g.time_interval*2 if g.time_interval <= 3600 else g.time_interval + 3600
        current_time = (datetime.datetime.now() + datetime.timedelta(seconds=-seconds)).strftime(
                "%Y-%m-%d %H:%M:%S")

        logger.info("push_json_data_list current_time %s" % current_time)

        # 获取 extract 数据
        extract_list = ExtractModel.get_data_by_time_status(current_time)

        # 通过 extract数据，查询 down_file数据
        di_down_file_list = DownFileModel.get_data_by_extract_list(extract_list)

        # 打印 抽取数据
        for down_file in di_down_file_list:
            logger.info("\n\ndown_file_info\ndown_file.id:%s\ndown_file.file_title:%s\ndown_file.extract_id:%s\ndown_file.extract_last_update_time:%s"
                        % (down_file.id, down_file.file_title, down_file.extract_id, down_file.extract_last_update_time))

        return di_down_file_list

    def get_file_info_and_extract_data(self, extract_id):
        """
        获取文件信息 和 抽取结果

        :param extract_id: extract_id list

        """

        # 用于存放抽取数据 和 文件信息
        result_output_data = []

        down_file_obj = DownFileModel.get_by_extract_id(extract_id=extract_id)

        # 文件信息不存在，则不获取抽取数据
        if not down_file_obj:
            logger.info("get_file_info_and_extract_data 文件信息不存在")
            raise ValueError("get_file_info_and_extract_data 文件信息不存在")

        header = get_idps_header(self.idps_token)
        extract_result = requests.get(idps_extract_result_url.format(extract_id=extract_id), headers=header)

        # 增加文件信息
        file_info_rule_extract = FileInfoExtractData(file_info=down_file_obj, extract_data=[])
        file_info_relation_extract = FileInfoExtractData(file_info=down_file_obj, extract_data=[])

        if extract_result.status_code == 200:
            extract_result_obj = extract_result.json()

            # 规则抽取结果
            rule_extract_result = extract_result_obj.get('item').get('result').get('tag_list')
            # 关系抽取结果
            relation_extract_result = extract_result_obj.get('item').get('result').get('relation_extract')

            # 规则抽取结果通过json 文件的形式传输
            # 获取 json 数据
            json_data = self.get_json_data(rule_extract_result)
            # 替换数据
            rule_extract_result = self.replace_rule_data(json_data, rule_extract_result)

            # 增加 pdf_path
            model_dict = down_file_obj.__dict__
            model_dict["pdf_path"] = extract_result_obj['item']['result']['pdf_path']

            # 增加抽取结果
            file_info_rule_extract.extract_data.extend(rule_extract_result)
            file_info_relation_extract.extract_data.extend(relation_extract_result)
        else:
            raise ValueError("get_file_info_and_extract_data 获取抽取信息失败")



        # 规则抽取 添加 schema_name 信息
        for rule_data in file_info_rule_extract.extract_data:
                rule_data.update(schema_name_dict.get(rule_data.get("tag_id"), {}))

        # 关系抽取 添加 schema_name 信息
        for relation_data in file_info_relation_extract.extract_data:
            relation_data.update(schema_name_dict.get(relation_data.get("id"), {}))

        return file_info_rule_extract, file_info_relation_extract

    def replace_rule_data(self, json_data, rule_extract_result):
        """
        通过json_data 替换数据，只对数据是 json路径的数据进行替换

        """

        # 将json 数据替换抽取数据中的 value
        for rule_extract in rule_extract_result[:]:
            data_value = json_data.get(str(rule_extract["tag_id"]), "")

            # 删除组合字段的数据
            if rule_extract['tag_id'] in relation_extract_tag_id_list:
                rule_extract_result.remove(rule_extract)
                continue

            # value 不是 json 路径的数据，不做处理
            if not rule_extract["value"].endswith(".json"):
                continue

            if isinstance(data_value, (dict, list)):
                rule_extract['value'] = json.dumps(data_value, ensure_ascii=False)
            else:
                rule_extract['value'] = data_value

        return rule_extract_result

    @staticmethod
    def get_json_data(rule_extract_result):
        """
        通过规则抽取结果，获取json 路径，并返回JSON 数据

        """

        json_data = ""

        for rule_extract in rule_extract_result:

            # 从规则抽取结果，获取json 路径，
            # /data/ 为路径约定结果
            # ".." + rule_extract['value'] 读取json, 通过挂载映射到data 路径下
            if rule_extract['value'].count("/data/") > 0:

                json_path = ".." + rule_extract['value']
                try:
                    json_data = json.load(open(json_path, "rb"))
                except Exception as e:
                    logger.error("get_json_data 从文件加载JSON 数据失败 %s " % json_path)
                    raise ValueError("get_json_data 从文件加载JSON 数据失败 %s " % json_path)
                break

        if json_data == "":
            logger.info("get_json_data 从抽取结果获取json 路径失败 ")
            raise ValueError("get_json_data 从抽取结果获取json 路径失败 ")

        return json_data

    def parser_table(self, file_info, element, data_frame_list):
        """
        处理表格的 value的 data部分，其他部分不变

        """
        element_value = json.loads(element['value'])
        element_value_data = element_value["data"]
        if len(element_value_data['mask']) > 0:
            res = gen_html_document(element_value_data)
            element_value_data = json.dumps(res, ensure_ascii=False)

        else:
            element_value_data = ""

        obj = get_common_part(element, file_info)

        obj["原文内容"] = get_location_data(element_value_data, element_value)
        obj["一级标题"] = get_location_data()
        obj["一级标题下正文"] = get_location_data()
        obj["二级标题"] = get_location_data()
        obj["二级标题下正文"] = get_location_data()
        obj["原文类型编号"] = get_location_data(element['txt_type_code'])
        obj["原文类型"] = get_location_data(element['txt_type'])

        data_frame_list.append(obj)

    def parse_first_title(self, file_info, element, result_list):
        """
        处理一级标题

        """
        data_list = json.loads(element['value'])
        for data_element in data_list:

            if data_element.get("title", "") == "":
                continue

            for child_element in data_element['title']['child']:

                obj = get_common_part(element, file_info)
                obj["原文内容"] = get_location_data(element['value'])
                obj["一级标题"] = get_location_data()
                obj["一级标题下正文"] = get_location_data()
                obj["二级标题"] = get_location_data()
                obj["二级标题下正文"] = get_location_data()
                obj["原文类型编号"] = get_location_data(element['txt_type_code'])
                obj["原文类型"] = get_location_data(element['txt_type'])

                if child_element.get("title", "") == "":
                    # 不存在一级标题
                    result_list.append(obj)
                    continue

                # 存在一级标题
                obj["一级标题"] = get_location_data(child_element['title']['text'], child_element['title'])
                obj["一级标题下正文"] = get_location_data(json.dumps(child_element['title']['child'], ensure_ascii=False))
                obj["二级标题"] = get_location_data()
                obj["二级标题下正文"] = get_location_data()

                result_list.append(obj)

    def parse_second_title(self, file_info, element, result_list):
        """
        处理二级标题
        """
        data_list = json.loads(element['value'])
        for data_element in data_list:

            if data_element.get("title", "") == "":
                continue

            for child_element in data_element['title']['child']:

                if child_element.get("title", "") == "":
                    continue

                for grandson_element in child_element['title']['child']:

                    obj = get_common_part(element, file_info)

                    obj["原文内容"] = get_location_data(element['value'])
                    obj["一级标题"] = get_location_data(child_element['title']['text'], child_element['title'])
                    obj["一级标题下正文"] = get_location_data(json.dumps(child_element['title']['child'], ensure_ascii=False))
                    obj["二级标题"] = get_location_data()
                    obj["二级标题下正文"] = get_location_data()
                    obj["原文类型编号"] = get_location_data(element['txt_type_code'])
                    obj["原文类型"] = get_location_data(element['txt_type'])

                    # 不存在二级标题
                    if grandson_element.get("title", "") == "":
                        result_list.append(obj)
                        continue

                    # 存在二级标题
                    obj["二级标题"] = get_location_data(grandson_element['title']['text'], grandson_element['title'])
                    obj["二级标题下正文"] = get_location_data(json.dumps(grandson_element['title']['child'], ensure_ascii=False))

                    result_list.append(obj)

    # @staticmethod
    # def move_null_data(obj, extra=[]):
    #     """
    #     除公共部分外，所有值为空则不返回该数据
    #
    #     """
    #
    #     # 公共部分
    #     k_list = ["uuid","Bulletin_ID","Schema_Name","announcementType","announcementTypeCode"
    #         ,"Source","fullName","publishDate","extractionDate","Rep_Type_Code"
    #         ,"Rep_Type","originFileUrl","info_type","title","fileUrl"
    #         ,"editor","md5Code","fileFormat","plate","market"
    #         ,"schemaVersion","schema_update_flag","Sub_ID ","Year","Valid_Flag","记录ID","年度","是否有效"]
    #
    #     # 添加额外数据
    #     if len(extra) > 0:
    #         k_list.extend(extra)
    #
    #     for k, v in obj.items():
    #         if k not in k_list and len(v) > 0:
    #             return False
    #
    #     return True

    @staticmethod
    def is_capital_takes_up(verify_str):
        """
        是否存在资金占用
        """

        no_rules = [
            r"不存在(其他)?资金被[主要控股股东、实际控制人及其控制的其他企业以借款、代偿债务、代垫款项或其他方式非经营性]{4,}占用的情形",
            r"款项已收回",
            r"占用情形已经消除",
            r"不存在资金被持有公司 5.00 % 以上股份的[主要控股股东、实际控制人及其控制的其他企业]{4,}占用的情况",
        ]

        for rule in no_rules:

            re_search = re.search(rule, verify_str)
            if re_search:
                return False

        return True

    @staticmethod
    def is_guarantee(verify_str):
        """
        是否存在担保情况
        """

        no_rules = [
            r"不存在为[主要控股股东、实际控制人及其控制的其他企业]{4,}进行(违规)?担保的情形",
            r"担保均已解除",
            r"不存在资金被[主要控股股东、实际控制人及其控制的其他企业以借款、代偿债务、代垫款项或其他方式]{4,}占用的情形[，,]?或者为[主要控股股东、实际控制人及其控制的其他企业]{4,}进行(违规)?担保的情形",
            r"不存在为持有公司 5.00 % 以上股份的[主要控股股东、实际控制人及其控制的其他企业]{4,}提供担保的情况",
        ]

        for rule in no_rules:

            re_search = re.search(rule, verify_str)
            if re_search:
                return False

        return True

    @staticmethod
    def is_compete(verify_str):
        """
        是否存在同业竞争
        """

        # is_rules = [
        #     r"存在为[\u4e00-\u9fa5]{3,15}提供反担保的情况",
        #     r"除[\u4e00-\u9fa5'\"（(]{3,70}代付(.*?)事项外",
        # ]
        no_rules = [
            r"[(（][一二三四五六七八九十]{1,2}[)）](发行人|公司)[与和]?控股股东、实际控制人及其控制的其他企业[之间与公司]{0,}不存在同业竞争",
            r"[(（][一二三四五六七八九十]{1,2}[)）](发行人|公司)[与和]?[主要控股股东实际控制人]{3,}及其控制的其他企业[之间与公司]{0,}不存在同业竞争",
            r"[(（][一二三四五六七八九十]{1,2}[)）]公司[与和]?控股股东、实际控制人的其他亲属控制的企业之间存在竞争关系",
            r"\d、(发行人|公司)[与和](控股股东|实际控制人)及其控制的其他企业[之间与公司]{0,}不存在同业竞争",
            r"\d、(发行人|公司)[与和]?控股股东(控制的其他企业)?不存在同业竞争",
            r"\d、(发行人|公司)[与和]?实际控制人控制的除控股股东外的其他企业不存在同业竞争",
            r"不存在与[控股股东、实际控制人及其控制的其他企业从事相同或相似]{4,}业务的情[形况]",
            r"不存在与(公司|发行人)从事相同[或、]?相似业务的情[形况]，[与公司发行人与公司控股股东、实际控制人及其控制的其他企业]{0,}不存在同业竞争",
            r"不存在与[控股股东、实际控制人及其控制的其他企业从事相同或相似]{4,}同业竞争的[形况]",
            r"不存在竞争关系，不存在同业竞争情况",
            r"[控股股东、实际控制人及其控制的其他企业]{4,}与公司不存在同业竞争关系。",
            r"不直接从事生产经营业务，与公司业务不存在相同或者相似的情况，不存在同业竞争。",
            r"及其控制的成员单位之间不存在同业竞争",
            r"与公司(之间)?不存在同业竞争的情[形况]",
            r"不存在从事与发行人相同[或、]?相似业务的情[形况]，不存在同业竞争情[形况]",
            r"未从事任何与公司相同[或、]?相似的业务，与本公司不存在同业竞争的情[形况]",
            r"其他企业与公司之间不存在同业竞争",
            r"发行人与持有发行人 5.00 % 以上股份的股东及其控制的其他企业间不存在同业竞争",
        ]

        for rule in no_rules:

            re_search = re.search(rule, verify_str)
            if re_search:
                return False

        return True

    def txt_table2html(self, txt_value_list):
        """
        处理原文内的表格

        """
        for data_element in txt_value_list[:]:

            # 丢弃段落内的 graph
            if data_element.get("graph", "") != "":
                txt_value_list.remove(data_element)
                continue

            #
            if data_element.get("table", "") != "":
                # 处理表格
                res = gen_html_document(data_element['table']["data"])
                data_element['table'] = get_location_data(res['table'], data_element['table'])
                continue

            # 存在title 递归处理
            if data_element.get("title", "") != "":
                self.txt_table2html(data_element['title']['child'])
                continue

    def merge_txt(self, chars_list):
        result_chars = ""
        result_locations = []

        for text in chars_list:

            if text.get("chars", "") != "":
                return text.get("chars", ""), text.get("locations", "")

            title = text.get("title", "")
            paragraph = text.get("paragraph", "")
            table = text.get("table", "")
            if title != "":
                result_chars += title.get("text", "").strip() + "\n"
                result_locations.extend(title.get("locations", [{
                                                "bboxes": "[]",
                                                "page_no": -1,
                                                "page_size": "[]"
                                                }]))

                chars, locations = self.merge_txt(title["child"])

                result_chars += chars.strip() + "\n"
                result_locations.extend(locations)

            elif paragraph != "":
                result_chars += paragraph.get("data", "").strip() + "\n"
                result_locations.extend(paragraph.get("locations", [{
                                                "bboxes": "[]",
                                                "page_no": -1,
                                                "page_size": "[]"
                                                }]))
            elif table != "":
                if isinstance(table,dict):
                    try:
                        table['chars']
                    except Exception as e :
                        element_value_data = table["data"]
                        if len(element_value_data['mask']) != 0:
                            res = gen_html_document(element_value_data)
                            table= {"chars": res["table"], "locations": table['locations']}

                    result_chars += table['chars'].strip() + "\n"
                    result_locations.extend(table.get("locations", [{
                        "bboxes": "[]",
                        "page_no": -1,
                        "page_size": "[]"
                    }]))
                else:
                    result_chars += table.strip() + "\n"
                    result_locations.extend([{
                                                "bboxes": "[]",
                                                "page_no": -1,
                                                "page_size": "[]"
                                                }])
        result_chars = re.sub(r"\n+", "\n", result_chars)
        return result_chars, result_locations

    def dispose_file_info_rule_extract(self, file_info_rule_extract):
        """
        处理 规则抽取数据

        """
        rule_extract = []

        file_info, extract_data = file_info_rule_extract.file_info, file_info_rule_extract.extract_data

        # 包括 原文、表格、图片、判断

        # 原文 表格
        rule_extract.extend(self.dispose_rule_text(file_info, extract_data, type_txt["tag_id"]))

        # 图片
        rule_extract.extend(self.dispose_rule_graph(file_info, extract_data, type_graph["tag_id"]))

        # kv表格
        rule_extract.extend(self.dispose_rule_info_issuer_info(file_info, extract_data, info_issuer_info["tag_id"]))
        rule_extract.extend(self.dispose_rule_info_issuer_intmd(file_info, extract_data, info_issuer_intmd["tag_id"]))
        rule_extract.extend(self.dispose_rule_info_release_profile(file_info, extract_data, info_release_profile["tag_id"]))

        # 处理 判断表格
        rule_extract.extend(self.dispose_rule_if_table(file_info, extract_data, if_table["tag_id"]))

        return rule_extract

    def dispose_rule_text(self, file_info, data_list, tag_id):
        """
        处理原文 表格

        """

        data_frame_list = []
        for element in data_list:

            # 只处理原文相关的数据
            if element.get("tag_id") in tag_id:

                # 表格转化html
                # 处理表格
                if element.get("tag_id") in (  # TypeTIdRelationEnum.table_release_profile,
                                             TypeTIdRelationEnum.table_issuer_info
                                             , TypeTIdRelationEnum.table_issuer_intmd
                                             , TypeTIdRelationEnum.table_five_cust_sell
                                             , TypeTIdRelationEnum.table_five_supplier_buy):

                    self.parser_table(file_info, element, data_frame_list)
                    continue
                else:
                    # 原文中的table 也要转
                    txt_value_list = json.loads(element['value'])
                    self.txt_table2html(txt_value_list)
                    element['value'] = json.dumps(txt_value_list, ensure_ascii=False)

                # 处理 一级标题 或 二级标题
                parse_first = element.get("parse_first", False)
                parse_second = element.get("parse_second", False)

                if parse_first:
                    self.parse_first_title(file_info, element, data_frame_list)
                    continue

                if parse_second:
                    self.parse_second_title(file_info, element, data_frame_list)
                    continue

                # 处理 其他原文
                obj = get_common_part(element, file_info)

                obj["原文内容"] = get_location_data(element['value'])
                obj["一级标题"] = get_location_data()
                obj["一级标题下正文"] = get_location_data()
                obj["二级标题"] = get_location_data()
                obj["二级标题下正文"] = get_location_data()
                obj["原文类型编号"] = get_location_data(element['txt_type_code'])
                obj["原文类型"] = get_location_data(element['txt_type'])

                data_frame_list.append(obj)

        for element in data_frame_list:
            # 原文内容
            chars_list = json.loads(element['原文内容']['chars'])
            if not isinstance(chars_list, dict):

                result_chars, result_locations = self.merge_txt(chars_list)
                element["原文内容"] = get_location_data(data=result_chars, locations=result_locations)

            # 一级标题下正文
            chars = element['一级标题下正文']['chars']
            if chars != "":
                chars_list = json.loads(element['一级标题下正文']['chars'])
                result_chars, result_locations = self.merge_txt(chars_list)
                element["一级标题下正文"] = get_location_data(data=result_chars, locations=result_locations)

            # 二级标题下正文
            chars = element['二级标题下正文']['chars']
            if chars != "":
                chars_list = json.loads(element['二级标题下正文']['chars'])
                result_chars, result_locations = self.merge_txt(chars_list)
                element["二级标题下正文"] = get_location_data(data=result_chars, locations=result_locations)

        get_empty_rule_data(file_info, tag_id, data_frame_list, "type_txt")
        return data_frame_list

    def dispose_rule_graph(self, file_info, data_list, tag_id: list):
        """
        处理图片
        """

        data_frame_list = []
        for element in data_list:
            if element.get("tag_id") in tag_id:

                obj = get_common_part(element, file_info)
                obj["图片类型编号"] = get_location_data()
                obj["图片类型"] = get_location_data()
                obj["图片内容"] = get_location_data()

                data_value = json.loads(element["value"])
                if len(data_value["data"]) > 0:
                    obj["图片类型编号"] = get_location_data(element['graph_type_code'])
                    obj["图片类型"] = get_location_data(element['graph_type'])
                    obj["图片内容"] = get_location_data(data_value["data"], data_value)

                data_frame_list.append(obj)

        get_empty_rule_data(file_info, tag_id, data_frame_list, "type_graph")
        return data_frame_list

    def dispose_rule_info_issuer_info(self, file_info, data_list, tag_id: list):
        """
         处理 科创板招股书发行人基本情况表 kv

        """

        data_frame_list = []

        for element in data_list:
            if element.get("tag_id") in tag_id:
                obj = get_common_part(element, file_info)

                data_value = json.loads(element["value"])

                obj["发行人中文名称"] = get_location_data(data_value["发行人中文名称"]["data"], data_value["发行人中文名称"])  # 发行人中文名称
                obj["发行人英文名称"] = get_location_data(data_value["发行人英文名称"]["data"], data_value["发行人英文名称"])  # 发行人英文名称
                obj["成立日期"] = get_location_data(data_value["成立日期"]["data"], data_value["成立日期"])  # 成立日期
                obj["有限公司成立日期"] = get_location_data(data_value["有限公司成立日期"]["data"], data_value["有限公司成立日期"])  # 有限公司成立日期
                obj["股份公司成立日期"] = get_location_data(data_value["股份公司成立日期"]["data"], data_value["股份公司成立日期"])  # 股份公司成立日期
                obj["注册资本"] = get_location_data(data_value["注册资本"]["data"], data_value["注册资本"])  # 注册资本
                obj["法定代表人"] = get_location_data(data_value["法定代表人"]["data"], data_value["法定代表人"])  # 法定代表人
                obj["注册地址"] = get_location_data(data_value["注册地址"]["data"], data_value["注册地址"])  # 注册地址
                obj["主要生产经营地址"] = get_location_data(data_value["主要生产经营地址"]["data"], data_value["主要生产经营地址"])  # 主要生产经营地址
                obj["控股股东"] = get_location_data(data_value["控股股东"]["data"], data_value["控股股东"])  # 控股股东
                obj["实际控制人"] = get_location_data(data_value["实际控制人"]["data"], data_value["实际控制人"])  # 实际控制人
                obj["行业分类"] = get_location_data(data_value["行业分类"]["data"], data_value["行业分类"])  # 行业分类
                obj["在其他场所（申请 ）挂牌或上市的情况"] = get_location_data(data_value["在其他场所（申请 ）挂牌或上市的情况"]["data"],  data_value["在其他场所（申请 ）挂牌或上市的情况"])  # 在其他场所（申请 ）挂牌或上市的情况
                obj["单位"] = get_location_data(data_value["单位"]["data"], data_value["单位"])  # 单位
                obj["币种"] = get_location_data(data_value["币种"]["data"], data_value["币种"])  # 币种

                data_frame_list.append(obj)

        for obj in data_frame_list:
            # 日期处理
            rpt_date = process_date(obj["成立日期"]["chars"])
            obj["成立日期"] = get_location_data(rpt_date, obj["成立日期"])
            rpt_date = process_date(obj["有限公司成立日期"]["chars"])
            obj["有限公司成立日期"] = get_location_data(rpt_date, obj["有限公司成立日期"])
            rpt_date = process_date(obj["股份公司成立日期"]["chars"])
            obj["股份公司成立日期"] = get_location_data(rpt_date, obj["股份公司成立日期"])

            # 单位处理
            unit, multiplier = process_unit(obj["单位"]["chars"])
            obj["单位"] = get_location_data(unit, obj["单位"])

            # 数量处理
            unit, multiplier = process_unit(obj["注册资本"]["chars"])
            # 数量处理
            num = process_num(obj["注册资本"]["chars"], multiplier)
            obj["注册资本"] = get_location_data(num, obj["注册资本"])

        get_empty_rule_data(file_info, tag_id, data_frame_list, "info_issuer_info")
        return data_frame_list

    def dispose_rule_info_issuer_intmd(self, file_info, data_list, tag_id: list):
        """
         处理 科创板招股书中介机构基本情况表 kv

        """

        data_frame_list = []
        for element in data_list:
            if element.get("tag_id") in tag_id:

                obj = get_common_part(element, file_info)

                data_value = json.loads(element["value"])
                obj["保荐人"] = get_location_data(data_value["保荐人"]["data"], data_value["保荐人"])  # 保荐人
                obj["主承销商"] = get_location_data(data_value["主承销商"]["data"], data_value["主承销商"])  # 主承销商
                obj["发行人律师"] = get_location_data(data_value["发行人律师"]["data"], data_value["发行人律师"])  # 发行人律师
                obj["其他承销机构"] = get_location_data(data_value["其他承销机构"]["data"], data_value["其他承销机构"])  # 其他承销机构
                obj["审计机构"] = get_location_data(data_value["审计机构"]["data"], data_value["审计机构"])  # 审计机构
                obj["评估机构"] = get_location_data(data_value["评估机构"]["data"], data_value["评估机构"])  # 评估机构
                obj["保荐人律师"] = get_location_data(data_value["保荐人律师"]["data"], data_value["保荐人律师"])  # 保荐人律师
                obj["主承销商律师"] = get_location_data(data_value["主承销商律师"]["data"], data_value["主承销商律师"])  # 主承销商律师
                obj["验资复核机构"] = get_location_data(data_value["验资复核机构"]["data"], data_value["验资复核机构"])  # 验资复核机构

                data_frame_list.append(obj)

        get_empty_rule_data(file_info, tag_id, data_frame_list, "info_issuer_intmd")
        return data_frame_list

    def dispose_rule_info_release_profile(self,  file_info, data_list, tag_id: list):
        """
         处理 科创板招股书发行概况表 kv

        """

        data_frame_list = []
        for element in data_list:
            if element.get("tag_id") in tag_id:

                obj = get_common_part(element, file_info)

                data_value = json.loads(element["value"])
                obj["股票种类"] = get_location_data(data_value["股票种类"]["data"], data_value["股票种类"])  # 股票种类
                obj["每股面值"] = get_location_data(data_value["每股面值"]["data"], data_value["每股面值"])  # 每股面值
                obj["发行股数上限"] = get_location_data(data_value["发行股数上限"]["data"], data_value["发行股数上限"])  # 发行股数上限
                obj["发行股数占发行后总股本的比例"] = get_location_data(data_value["发行股数占发行后总股本的比例"]["data"], data_value["发行股数占发行后总股本的比例"])  # 发行股数占发行后总股本的比例
                obj["超额配售上限"] = get_location_data(data_value["超额配售上限"]["data"], data_value["超额配售上限"])  # 超额配售上限
                obj["其中：发行新股数量"] = get_location_data(data_value["其中：发行新股数量"]["data"], data_value["其中：发行新股数量"])  # 其中：发行新股数量
                obj["其中：发行新股数量占发行后总股本的比例"] = get_location_data(data_value["其中：发行新股数量占发行后总股本的比例"]["data"], data_value["其中：发行新股数量占发行后总股本的比例"])  # 其中：发行新股数量占发行后总股本的比例
                obj["股东公开发售股份数量"] = get_location_data(data_value["股东公开发售股份数量"]["data"], data_value["股东公开发售股份数量"])  # 股东公开发售股份数量
                obj["股东公开发售股份数量占发行后总股本的比例"] = get_location_data(data_value["股东公开发售股份数量占发行后总股本的比例"]["data"], data_value["股东公开发售股份数量占发行后总股本的比例"])  # 股东公开发售股份数量占发行后总股本的比例
                obj["发行后总股本上限"] = get_location_data(data_value["发行后总股本上限"]["data"], data_value["发行后总股本上限"])  # 发行后总股本上限
                obj["每股发行价格"] = get_location_data(data_value["每股发行价格"]["data"], data_value["每股发行价格"])  # 每股发行价格
                obj["发行人高管、员工拟参与战略配售情况（如有）"] = get_location_data(data_value["发行人高管、员工拟参与战略配售情况（如有）"]["data"], data_value["发行人高管、员工拟参与战略配售情况（如有）"])  # 发行人高管、员工拟参与战略配售情况（如有）
                obj["保荐人相关子公司拟参与战略配售情况（如有）"] = get_location_data(data_value["保荐人相关子公司拟参与战略配售情况（如有）"]["data"], data_value["保荐人相关子公司拟参与战略配售情况（如有）"] )  # 保荐人相关子公司拟参与战略配售情况（如有）
                obj["发行市盈率"] = get_location_data(data_value["发行市盈率"]["data"], data_value["发行市盈率"])  # 发行市盈率
                obj["发行前每股收益"] = get_location_data(data_value["发行前每股收益"]["data"], data_value["发行前每股收益"])  # 发行前每股收益
                obj["发行后每股收益"] = get_location_data(data_value["发行后每股收益"]["data"], data_value["发行后每股收益"])  # 发行后每股收益
                obj["发行前每股净资产"] = get_location_data(data_value["发行前每股净资产"]["data"], data_value["发行前每股净资产"])  # 发行前每股净资产
                obj["发行后每股净资产"] = get_location_data(data_value["发行后每股净资产"]["data"], data_value["发行后每股净资产"])  # 发行后每股净资产
                obj["发行市净率"] = get_location_data(data_value["发行市净率"]["data"], data_value["发行市净率"])  # 发行市净率
                obj["发行方式"] = get_location_data(data_value["发行方式"]["data"], data_value["发行方式"])  # 发行方式
                obj["发行对象"] = get_location_data(data_value["发行对象"]["data"], data_value["发行对象"])  # 发行对象
                obj["承销方式"] = get_location_data(data_value["承销方式"]["data"], data_value["承销方式"])  # 承销方式
                obj["拟公开发售股份的股东名称"] = get_location_data(data_value["拟公开发售股份的股东名称"]["data"], data_value["拟公开发售股份的股东名称"])  # 拟公开发售股份的股东名称
                obj["拟公开发售股份的股东持股数量"] = get_location_data(data_value["拟公开发售股份的股东持股数量"]["data"], data_value["拟公开发售股份的股东持股数量"])  # 拟公开发售股份的股东持股数量
                obj["发行费用分摊原则"] = get_location_data(data_value["发行费用分摊原则"]["data"], data_value["发行费用分摊原则"])  # 发行费用分摊原则
                obj["募集资金总额"] = get_location_data(data_value["募集资金总额"]["data"], data_value["募集资金总额"])  # 募集资金总额
                obj["募集资金净额"] = get_location_data(data_value["募集资金净额"]["data"], data_value["募集资金净额"])  # 募集资金净额
                obj["募集资金投资项目"] = get_location_data(data_value["募集资金投资项目"]["data"], data_value["募集资金投资项目"])  # 募集资金投资项目
                obj["发行费用概算：总计"] = get_location_data(data_value["发行费用概算.总计"]["data"], data_value["发行费用概算.总计"])  # 发行费用概算.总计
                obj["发行费用概算：承销费"] = get_location_data(data_value["发行费用概算.承销费"]["data"], data_value["发行费用概算.承销费"])  # 发行费用概算.承销费
                obj["发行费用概算：保荐费"] = get_location_data(data_value["发行费用概算.保荐费"]["data"], data_value["发行费用概算.保荐费"])  # 发行费用概算.保荐费
                obj["发行费用概算：保荐及承销费"] = get_location_data(data_value["发行费用概算.保荐及承销费"]["data"], data_value["发行费用概算.保荐及承销费"])  # 发行费用概算.保荐及承销费
                obj["发行费用概算：审计费"] = get_location_data(data_value["发行费用概算.审计费"]["data"], data_value["发行费用概算.审计费"])  # 发行费用概算.审计费
                obj["发行费用概算：审计及验资费"] = get_location_data(data_value["发行费用概算.审计及验资费"]["data"], data_value["发行费用概算.审计及验资费"])  # 发行费用概算.审计及验资费
                obj["发行费用概算：评估费"] = get_location_data(data_value["发行费用概算.评估费"]["data"], data_value["发行费用概算.评估费"])  # 发行费用概算.评估费
                obj["发行费用概算：律师费"] = get_location_data(data_value["发行费用概算.律师费"]["data"], data_value["发行费用概算.律师费"])  # 发行费用概算.律师费
                obj["发行费用概算：信息披露费"] = get_location_data(data_value["发行费用概算.信息披露费"]["data"], data_value["发行费用概算.信息披露费"])  # 发行费用概算.信息披露费
                obj["发行费用概算：发行手续费"] = get_location_data(data_value["发行费用概算.发行手续费"]["data"], data_value["发行费用概算.发行手续费"])  # 发行费用概算.发行手续费
                obj["发行费用概算：发行股份登记托管费"] = get_location_data(data_value["发行费用概算.发行股份登记托管费"]["data"], data_value["发行费用概算.发行股份登记托管费"])  # 发行费用概算.发行股份登记托管费
                obj["发行费用概算：其他费用"] = get_location_data(data_value["发行费用概算.其他费用"]["data"], data_value["发行费用概算.其他费用"])  # 发行费用概算.其他费用
                obj["发行费用概算：信息披露及其他费用"] = get_location_data(data_value["发行费用概算.信息披露及其他费用"]["data"], data_value["发行费用概算.信息披露及其他费用"])  # 发行费用概算.信息披露及其他费用
                obj["刊登发行公告日期"] = get_location_data(data_value["刊登发行公告日期"]["data"], data_value["刊登发行公告日期"])  # 刊登发行公告日期
                obj["开始询价推介日期"] = get_location_data(data_value["开始询价推介日期"]["data"], data_value["开始询价推介日期"] )  # 开始询价推介日期
                obj["刊登定价公告日期"] = get_location_data(data_value["刊登定价公告日期"]["data"], data_value["刊登定价公告日期"])  # 刊登定价公告日期
                obj["申购日期"] = get_location_data(data_value["申购日期"]["data"], data_value["申购日期"])  # 申购日期
                obj["缴款日期"] = get_location_data(data_value["缴款日期"]["data"], data_value["缴款日期"])  # 缴款日期
                obj["股票上市日期"] = get_location_data(data_value["股票上市日期"]["data"], data_value["股票上市日期"])  # 股票上市日期

                data_frame_list.append(obj)

        for obj in data_frame_list:
            # 单位处理
            unit, multiplier = process_unit(obj["每股面值"]["chars"])
            # 数量处理
            num = process_num(obj["每股面值"]["chars"], multiplier)
            obj["每股面值"] = get_location_data(num, obj["每股面值"])

            # 发行股数上限
            unit, multiplier = process_unit(obj["其中：发行新股数量"]["chars"])
            # 数量处理
            num = process_num(obj["其中：发行新股数量"]["chars"], multiplier)
            obj["其中：发行新股数量"] = get_location_data(num, obj["其中：发行新股数量"])
            # 数量处理
            num = process_num(obj["其中：发行新股数量占发行后总股本的比例"]["chars"], 1)
            obj["其中：发行新股数量占发行后总股本的比例"] = get_location_data(num, obj["其中：发行新股数量占发行后总股本的比例"])

            # 其中：发行新股数量
            unit, multiplier = process_unit(obj["发行股数上限"]["chars"])
            # 数量处理
            num = process_num(obj["发行股数上限"]["chars"], multiplier)
            obj["发行股数上限"] = get_location_data(num, obj["发行股数上限"])
            # 数量处理
            num = process_num(obj["发行股数占发行后总股本的比例"]["chars"], 1)
            obj["发行股数占发行后总股本的比例"] = get_location_data(num, obj["发行股数占发行后总股本的比例"])

            # 股东公开发售股份数量
            unit, multiplier = process_unit(obj["股东公开发售股份数量"]["chars"])
            # 数量处理
            num = process_num(obj["股东公开发售股份数量"]["chars"], multiplier)
            obj["股东公开发售股份数量"] = get_location_data(num, obj["股东公开发售股份数量"])
            # 数量处理
            num = process_num(obj["股东公开发售股份数量占发行后总股本的比例"]["chars"], 1)
            obj["股东公开发售股份数量占发行后总股本的比例"] = get_location_data(num, obj["股东公开发售股份数量占发行后总股本的比例"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行后总股本上限"]["chars"])
            # 数量处理
            num = process_num(obj["发行后总股本上限"]["chars"], multiplier)
            obj["发行后总股本上限"] = get_location_data(num, obj["发行后总股本上限"])

            # 单位处理
            unit, multiplier = process_unit(obj["每股发行价格"]["chars"])
            # 数量处理
            num = process_num(obj["每股发行价格"]["chars"], multiplier)
            obj["每股发行价格"] = get_location_data(num, obj["每股发行价格"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行前每股收益"]["chars"])
            # 数量处理
            num = process_num(obj["发行前每股收益"]["chars"], multiplier)
            obj["发行前每股收益"] = get_location_data(num, obj["发行前每股收益"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行后每股收益"]["chars"])
            # 数量处理
            num = process_num(obj["发行后每股收益"]["chars"], multiplier)
            obj["发行后每股收益"] = get_location_data(num, obj["发行后每股收益"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行前每股净资产"]["chars"])
            # 数量处理
            num = process_num(obj["发行前每股净资产"]["chars"], multiplier)
            obj["发行前每股净资产"] = get_location_data(num, obj["发行前每股净资产"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行后每股净资产"]["chars"])
            # 数量处理
            num = process_num(obj["发行后每股净资产"]["chars"], multiplier)
            obj["发行后每股净资产"] = get_location_data(num, obj["发行后每股净资产"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行市盈率"]["chars"])
            # 数量处理
            num = process_num(obj["发行市盈率"]["chars"], multiplier)
            obj["发行市盈率"] = get_location_data(num, obj["发行市盈率"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行市净率"]["chars"])
            # 数量处理
            num = process_num(obj["发行市净率"]["chars"], multiplier)
            obj["发行市净率"] = get_location_data(num, obj["发行市净率"])

            # 单位处理
            unit, multiplier = process_unit(obj["拟公开发售股份的股东持股数量"]["chars"])
            # 数量处理
            num = process_num(obj["拟公开发售股份的股东持股数量"]["chars"], multiplier)
            obj["拟公开发售股份的股东持股数量"] = get_location_data(num, obj["拟公开发售股份的股东持股数量"])

            # 单位处理
            unit, multiplier = process_unit(obj["募集资金总额"]["chars"])
            # 数量处理
            num = process_num(obj["募集资金总额"]["chars"], multiplier)
            obj["募集资金总额"] = get_location_data(num, obj["募集资金总额"])

            # 单位处理
            unit, multiplier = process_unit(obj["募集资金净额"]["chars"])
            # 数量处理
            num = process_num(obj["募集资金净额"]["chars"], multiplier)
            obj["募集资金净额"] = get_location_data(num, obj["募集资金净额"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：总计"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：总计"]["chars"], multiplier)
            obj["发行费用概算：总计"] = get_location_data(num, obj["发行费用概算：总计"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：承销费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：承销费"]["chars"], multiplier)
            obj["发行费用概算：承销费"] = get_location_data(num, obj["发行费用概算：承销费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：保荐费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：保荐费"]["chars"], multiplier)
            obj["发行费用概算：保荐费"] = get_location_data(num, obj["发行费用概算：保荐费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：保荐及承销费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：保荐及承销费"]["chars"], multiplier)
            obj["发行费用概算：保荐及承销费"] = get_location_data(num, obj["发行费用概算：保荐及承销费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：审计费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：审计费"]["chars"], multiplier)
            obj["发行费用概算：审计费"] = get_location_data(num, obj["发行费用概算：审计费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：审计及验资费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：审计及验资费"]["chars"], multiplier)
            obj["发行费用概算：审计及验资费"] = get_location_data(num, obj["发行费用概算：审计及验资费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：评估费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：评估费"]["chars"], multiplier)
            obj["发行费用概算：评估费"] = get_location_data(num, obj["发行费用概算：评估费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：律师费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：律师费"]["chars"], multiplier)
            obj["发行费用概算：律师费"] = get_location_data(num, obj["发行费用概算：律师费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：信息披露费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：信息披露费"]["chars"], multiplier)
            obj["发行费用概算：信息披露费"] = get_location_data(num, obj["发行费用概算：信息披露费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：发行手续费"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：发行手续费"]["chars"], multiplier)
            obj["发行费用概算：发行手续费"] = get_location_data(num, obj["发行费用概算：发行手续费"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：其他费用"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：其他费用"]["chars"], multiplier)
            obj["发行费用概算：其他费用"] = get_location_data(num, obj["发行费用概算：其他费用"])

            # 单位处理
            unit, multiplier = process_unit(obj["发行费用概算：信息披露及其他费用"]["chars"])
            # 数量处理
            num = process_num(obj["发行费用概算：信息披露及其他费用"]["chars"], multiplier)
            obj["发行费用概算：信息披露及其他费用"] = get_location_data(num, obj["发行费用概算：信息披露及其他费用"])

        get_empty_rule_data(file_info, tag_id, data_frame_list, "info_release_profile")
        return data_frame_list

    def dispose_rule_if_table(self, file_info, data_list, tag_id: list):
        """
        处理 判断表格

        """

        data_frame_list = []
        for element in data_list:
            if element.get("tag_id") in tag_id:

                obj = get_common_part(element, file_info)

                data_value = json.loads(element["value"])

                result_chars, result_locations = self.merge_txt(data_value)

                obj["判断类型编号"] = get_location_data(element['if_type_code'])
                obj["判断类型"] = get_location_data(element['if_type'])
                obj["判断内容"] = get_location_data(data=result_chars, locations=result_locations)
                obj["判断结果"] = get_location_data("N")

                # 通过合并文本判定是 或者否
                if element.get("tag_id") == TypeTIdRelationEnum.if_cash_dominate:
                    if self.is_capital_takes_up(result_chars) or self.is_guarantee(result_chars):
                        obj["判断结果"] = get_location_data("Y")

                elif element.get("tag_id") == TypeTIdRelationEnum.if_compete:
                    if self.is_compete(result_chars):
                        obj["判断结果"] = get_location_data("Y")

                data_frame_list.append(obj)

        get_empty_rule_data(file_info, tag_id, data_frame_list, "if_table")
        return data_frame_list

    def dispose_file_info_relation_extract(self, file_info_relation_extract):
        """
        处理 关系抽取数据

        """

        relation_extract = []

        file_info, extract_data = file_info_relation_extract.file_info, file_info_relation_extract.extract_data

        # 处理信息点
        # 股本情况表
        relation_extract.extend(self.dispose_relation_info_point_issue_shr(file_info, extract_data
                                                                           , info_point_issue_shr["group_id"]))

        # 兼职情况表
        relation_extract.extend(self.dispose_relation_info_point_cstdn_part_time(file_info, extract_data
                                                                                 ,  info_point_cstdn_part_time["group_id"]))

        # 对外投资情况表
        relation_extract.extend(self.dispose_relation_info_point_cstdn_invest(file_info, extract_data
                                                                                 ,  info_point_cstdn_invest["group_id"]))
        # 前五客户情况表
        relation_extract.extend(self.dispose_relation_info_point_five_cust_sell(file_info, extract_data
                                                                                 ,  info_point_five_cust_sell["group_id"]))
        # 前五供应商情况表
        relation_extract.extend(self.dispose_relation_info_point_five_supplier_buy(file_info, extract_data
                                                                                 ,  info_point_five_supplier_buy["group_id"]))
        # 财务状况分析表
        relation_extract.extend(self.dispose_relation_info_point_fin_fare(file_info, extract_data
                                                                                 ,  info_point_fin_fare["group_id"]))
        # 核心技术产品占比
        relation_extract.extend(self.dispose_relation_info_point_core_prod_ratio(file_info, extract_data
                                                                                 ,  info_point_core_prod_ratio["group_id"]))

        return relation_extract

    def dispose_relation_info_point_issue_shr(self, file_info, data_list, group_id):
        """
        股本情况表
        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info)

                    obj["股东名称"] = get_location_data()
                    obj["发行前持股数量"] = get_location_data()
                    obj["发行前持股比例"] = get_location_data()
                    obj["发行后持股数量"] = get_location_data()
                    obj["发行后持股比例"] = get_location_data()
                    obj["发行前公司的总股本"] = get_location_data()
                    obj["发行后公司的总股本"] = get_location_data()
                    obj["股本单位"] = get_location_data()
                    obj["本次拟发行人民币普通股数量"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.ipis_name == element_value["tag_id"]:
                            obj["股东名称"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_pre_num == element_value["tag_id"]:
                            obj["发行前持股数量"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_pre_ratio == element_value["tag_id"]:
                            obj["发行前持股比例"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_after_num == element_value["tag_id"]:
                            obj["发行后持股数量"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_after_ratio == element_value["tag_id"]:
                            obj["发行后持股比例"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_pre_total_num == element_value["tag_id"]:
                            obj["发行前公司的总股本"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_total_num == element_value["tag_id"]:
                            obj["发行后公司的总股本"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_unit == element_value["tag_id"]:
                            obj["股本单位"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipis_num == element_value["tag_id"]:
                            obj["本次拟发行人民币普通股数量"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        for obj in data_frame_list:

            # 单位处理
            unit, multiplier = process_unit(obj["股本单位"]["chars"])
            obj["股本单位"] = get_location_data(unit, obj["股本单位"])

            # 数量处理
            num = process_num(obj["发行前持股数量"]["chars"], multiplier)
            obj["发行前持股数量"] = get_location_data(num, obj["发行前持股数量"])

            num = process_num(obj["发行后持股数量"]["chars"], multiplier)
            obj["发行后持股数量"] = get_location_data(num, obj["发行后持股数量"])

            num = process_num(obj["发行前公司的总股本"]["chars"], multiplier)
            obj["发行前公司的总股本"] = get_location_data(num, obj["发行前公司的总股本"])

            num = process_num(obj["本次拟发行人民币普通股数量"]["chars"], multiplier)
            obj["本次拟发行人民币普通股数量"] = get_location_data(num, obj["本次拟发行人民币普通股数量"])

            num = process_num(obj["发行后公司的总股本"]["chars"], multiplier)
            obj["发行后公司的总股本"] = get_location_data(num, obj["发行后公司的总股本"])

            num = process_num(obj["发行前持股比例"]["chars"], 1)
            obj["发行前持股比例"] = get_location_data(num, obj["发行前持股比例"])

            num = process_num(obj["发行后持股比例"]["chars"], 1)
            obj["发行后持股比例"] = get_location_data(num, obj["发行后持股比例"])

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def dispose_relation_info_point_cstdn_part_time(self, file_info, data_list, group_id):
        """
        兼职情况表

        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info)

                    obj["人员姓名"] = get_location_data()
                    obj["公司职务"] = get_location_data()
                    obj["兼职单位"] = get_location_data()
                    obj["兼职职务"] = get_location_data()
                    obj["与公司的关联关系"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.ipcpt_name == element_value["tag_id"]:
                            obj["人员姓名"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipcpt_company_office == element_value["tag_id"]:
                            obj["公司职务"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipcpt_part_time_company == element_value["tag_id"]:
                            obj["兼职单位"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipcpt_part_time_job == element_value["tag_id"]:
                            obj["兼职职务"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipcpt_correlation == element_value["tag_id"]:
                            obj["与公司的关联关系"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def dispose_relation_info_point_cstdn_invest(self, file_info, data_list, group_id):
        """
        对外投资情况表
        
        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info)

                    obj["人员姓名"] = get_location_data()
                    obj["公司职务"] = get_location_data()
                    obj["被投资公司"] = get_location_data()
                    obj["持股比例"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.ipci_name == element_value["tag_id"]:
                            obj["人员姓名"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipci_company_office == element_value["tag_id"]:
                            obj["公司职务"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipci_investee_company == element_value["tag_id"]:
                            obj["被投资公司"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipci_ratio == element_value["tag_id"]:
                            obj["持股比例"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        for obj in data_frame_list:

            num = process_num(obj["持股比例"]["chars"], 1)
            obj["持股比例"] = get_location_data(num, obj["持股比例"])

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def dispose_relation_info_point_five_cust_sell(self, file_info, data_list, group_id):
        """
        前五客户情况表

        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info, have_year=False)

                    obj["序号"] = get_location_data()
                    obj["报告期"] = get_location_data()
                    obj["业务线名称"] = get_location_data()
                    obj["对象公司名称"] = get_location_data()
                    obj["客户名称"] = get_location_data()
                    obj["销售产品类型"] = get_location_data()
                    obj["销售金额"] = get_location_data()
                    obj["占营业收入的比例"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.ipfcs_company_name == element_value["tag_id"]:
                            obj["对象公司名称"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_num == element_value["tag_id"]:
                            obj["序号"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_name == element_value["tag_id"]:
                            obj["客户名称"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_type == element_value["tag_id"]:
                            obj["销售产品类型"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_amount == element_value["tag_id"]:
                            obj["销售金额"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_ratio == element_value["tag_id"]:
                            obj["占营业收入的比例"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_unit == element_value["tag_id"]:
                            obj["单位"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_reporting_period == element_value["tag_id"]:
                            obj["报告期"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfcs_business_line == element_value["tag_id"]:
                            obj["业务线名称"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        for obj in data_frame_list:

            if obj.get("单位","") == "":
                obj["单位"] = get_location_data("元")

            # 报告期处理
            rpt_date = process_date(obj["报告期"]["chars"])
            obj["报告期"] = get_location_data(rpt_date, obj["报告期"])

            unit, multiplier = process_unit(obj["单位"]["chars"])
            obj["单位"] = unit

            # 数量处理
            num = process_num(obj["销售金额"]["chars"], multiplier)
            obj["销售金额"] = get_location_data(num, obj["销售金额"])
            num = process_num(obj["占营业收入的比例"]["chars"], 1)
            obj["占营业收入的比例"] = get_location_data(num, obj["占营业收入的比例"])

            obj["币种"] = get_location_data("人民币")

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def dispose_relation_info_point_five_supplier_buy(self, file_info, data_list, group_id):
        """
        前五供应商情况表

        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info, have_year=False)

                    obj["序号"] = get_location_data()
                    obj["报告期"] = get_location_data()
                    obj["对象公司名称"] = get_location_data()
                    obj["供应商名称"] = get_location_data()
                    obj["采购产品类型"] = get_location_data()
                    obj["采购金额"] = get_location_data()
                    obj["占采购总额的比例"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.ipfsb_reporting_period == element_value["tag_id"]:
                            obj["报告期"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_company_name == element_value["tag_id"]:
                            obj["对象公司名称"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_num == element_value["tag_id"]:
                            obj["序号"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_name == element_value["tag_id"]:
                            obj["供应商名称"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_type == element_value["tag_id"]:
                            obj["采购产品类型"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_amount == element_value["tag_id"]:
                            obj["采购金额"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_ratio == element_value["tag_id"]:
                            obj["占采购总额的比例"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipfsb_unit == element_value["tag_id"]:
                            obj["单位"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        for obj in data_frame_list:

            if obj.get("单位","") == "":
                obj["单位"] = get_location_data("元")

            # 报告期处理
            rpt_date = process_date(obj["报告期"]["chars"])
            obj["报告期"] = get_location_data(rpt_date, obj["报告期"])

            unit, multiplier = process_unit(obj["单位"]["chars"])
            obj["单位"] = unit

            # 数量处理
            num = process_num(obj["采购金额"]["chars"], multiplier)
            obj["采购金额"] = get_location_data(num, obj["采购金额"])
            num = process_num(obj["占采购总额的比例"]["chars"], 1)
            obj["占采购总额的比例"] = get_location_data(num, obj["占采购总额的比例"])

            obj["币种"] = get_location_data("人民币")

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def dispose_relation_info_point_fin_fare(self, file_info, data_list, group_id):
        """
        财务状况分析表

        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info, have_year=False)

                    obj["报告期"] = get_location_data()
                    obj["项目名称"] = get_location_data()
                    obj["项目金额"] = get_location_data()
                    obj["项目金额占比"] = get_location_data()
                    obj["科目类型编码"] = get_location_data()
                    obj["科目类型"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.ipff_reporting_period == element_value["tag_id"]:
                            obj["报告期"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipff_name == element_value["tag_id"]:
                            obj["项目名称"] = get_info_location_data(element)

                            obj["科目类型编码"] = "000030"
                            obj["科目类型"] = "财务费用"

                        elif TypeTIdRelationEnum.ipff_amount == element_value["tag_id"]:
                            obj["项目金额"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipff_ratio == element_value["tag_id"]:
                            obj["项目金额占比"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipff_unit == element_value["tag_id"]:
                            obj["单位"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        for obj in data_frame_list:

            if obj.get("单位","") == "":
                obj["单位"] = get_location_data("元")

            # 报告期处理
            rpt_date = process_date(obj["报告期"]["chars"])
            obj["报告期"] = get_location_data(rpt_date, obj["报告期"])

            unit, multiplier = process_unit(obj["单位"]["chars"])
            obj["单位"] = unit

            # 数量处理
            num = process_num(obj["项目金额"]["chars"], multiplier)
            obj["项目金额"] = get_location_data(num, obj["项目金额"])
            num = process_num(obj["项目金额占比"]["chars"], 1)
            obj["项目金额占比"] = get_location_data(num, obj["项目金额占比"])

            obj["币种"] = get_location_data("人民币")

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def dispose_relation_info_point_core_prod_ratio(self, file_info, data_list, group_id):
        """
        核心技术产品占比

        """

        data_frame_list = []

        for info_category in data_list:

            # 处理指定的信息点类型
            if info_category.get("id", 0) == group_id:

                # 处理信息点
                for info_group_element in info_category.get("children", []):

                    # 确保下游收到完整的数据
                    obj = get_common_part(info_category, file_info, have_year=False)

                    obj["报告期"] = get_location_data()
                    obj["项目名称"] = get_location_data()
                    obj["项目金额"] = get_location_data()
                    obj["核心技术产品收入"] = get_location_data()
                    obj["主营业务收入"] = get_location_data()
                    obj["核心技术产品收入占主营业务收入比例"] = get_location_data()

                    for element in info_group_element.get("children", []):

                        element_value = element['value'][0]

                        if TypeTIdRelationEnum.info_core_prod_ratio_rpt_date == element_value["tag_id"]:
                            obj["报告期"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.info_core_prod_ratio_item_name == element_value["tag_id"]:
                            obj["项目名称"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.info_core_prod_ratio_core_prod_amt == element_value["tag_id"]:
                            obj["核心技术产品收入"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.info_core_prod_ratio_main_biz_amt == element_value["tag_id"]:
                            obj["主营业务收入"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.info_core_prod_ratio_core_prod_ratio == element_value["tag_id"]:
                            obj["核心技术产品收入占主营业务收入比例"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.info_core_prod_ratio_item_amt == element_value["tag_id"]:
                            obj["项目金额"] = get_info_location_data(element)

                        elif TypeTIdRelationEnum.ipff_unit == element_value["tag_id"]:
                            obj["单位"] = get_info_location_data(element)

                    data_frame_list.append(obj)

        for obj in data_frame_list:
            if obj.get("单位","")=="":
                obj["单位"] = get_location_data("元")

            # 报告期处理
            rpt_date = process_date(obj["报告期"]["chars"])
            obj["报告期"] = get_location_data(rpt_date, obj["报告期"])

            unit, multiplier = process_unit(obj["单位"]["chars"])
            obj["单位"] = unit

            # 数量处理
            num = process_num(obj["核心技术产品收入"]["chars"], multiplier)
            obj["项目金额"] = get_location_data(num, obj["核心技术产品收入"])

            num = process_num(obj["主营业务收入"]["chars"], multiplier)
            obj["主营业务收入"] = get_location_data(num, obj["主营业务收入"])

            num = process_num(obj["项目金额"]["chars"], multiplier)
            obj["项目金额"] = get_location_data(num, obj["项目金额"])

            num = process_num(obj["核心技术产品收入占主营业务收入比例"]["chars"], 1)
            obj["核心技术产品收入占主营业务收入比例"] = get_location_data(num, obj["核心技术产品收入占主营业务收入比例"])

            obj["币种"] = get_location_data("人民币")

        get_empty_relation_data(file_info, group_id, data_frame_list)
        return data_frame_list

    def push_kafka(self, push_json_data_list, topic):

        logger.info("[PUSH Data TO KAFKA]: push_kafka start")

        for json_data in push_json_data_list:

            fail_flag = False
            producer = g.producer

            try:
                logger.info("[PUSH Data send]: topic %s" % topic)
                logger.info("[PUSH Data json_data]: %s " % json_data)
                # producer.send(topic, json_data).add_callback(self.send_success).add_errback(self.send_error)
                # producer.flush()
                future = producer.send(topic, json_data)
                record_metadata = future.get(timeout=10)  # 同步确认消费
                partition = record_metadata.partition  # 数据所在的分区
                offset = record_metadata.offset  # 数据所在分区的位置
                print("save success, partition: {}, offset: {}".format(partition, offset))
            except Exception as e:
                fail_flag = True
                logger.warning("[PUSH Data WARN]: {}".format(repr(e)))

            # producer.close()
            if not fail_flag:
                logger.info("[PUSH Data TO KAFKA]: success")

        logger.info("[PUSH Data TO KAFKA]: push_kafka over")
        return

    # def send_success(self, *args, **kwargs):
    #     """异步发送成功回调函数"""
    #     print(args)
    #     print(kwargs)
    #     print('save success')
    #     return
    #
    # def send_error(self, *args, **kwargs):
    #     """异步发送错误回调函数"""
    #     print(args)
    #     print(kwargs)
    #     print('save error')
    #     return
