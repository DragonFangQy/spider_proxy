# coding=utf-8
"""
@FileName：push_kafka_temporary_announcement
@ProjectName：
@CreateTime：2022/5/18 下午8:08
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
import json
from collections import namedtuple

import requests

from configs.sse_info3_conf import idps_extract_result_url
from entities.tags_entity import NodeTypeEnum
from initialization.logger_process import logger
from models.data_input_model import DownFileModel
from models.tags_model import TagsModel
from utils.sse_info3_util import get_idps_header, FileInfoExtractData, get_common_part


class PushKafkaTemporaryAnnouncementService(object):

    def __init__(self, idps_token):
        self.idps_token = idps_token
        self.doc_type_id = 0
        self.rule_tags_model, self.relation_tags_model = None, None

    def dispose_temporary_announcement(self, extract_id):
        file_info, rule_extract, relation_extract = self.get_file_info_and_extract_data(extract_id)

        self.doc_type_id = file_info.doc_type_id
        self.rule_tags_model, self.relation_tags_model = self.get_all_tags()

        # 处理 metas
        metas = get_common_part(None, file_info)

        rule_data = self.dispose_rule_extract(rule_extract)

        relation_data = self.dispose_relation_extract(relation_extract)

        rule_data.update(relation_data)
        file_json_data_dict = {"metas": metas, "results": [rule_data]}
        file_json_data = json.dumps(file_json_data_dict, ensure_ascii=False)

        return file_json_data

    def get_all_tags(self):
        count, tags_model = TagsModel.get_by_filter(active_only=False, tag_type_id=self.doc_type_id)
        rule_tags_model = {}
        relation_tags_model = {}

        for element_model in tags_model:

            # 实体字段
            # id: entity
            if self.is_rule_tags(element_model):
                rule_tags_model[element_model.id] = element_model
                continue

            # 组合字段构建 {parent_id:{group:entity , tag:entity_list }}
            # 组合字段的实体字段
            if self.is_relation_tags_child(element_model):
                group_id = int(element_model.parent_id[1:-1])
                group_dict = relation_tags_model.get(group_id, {})
                tag_list = group_dict.get(NodeTypeEnum.tag.value, [])
                tag_list.append(element_model)
                group_dict[NodeTypeEnum.tag.value] = tag_list
                relation_tags_model.update({group_id: group_dict})
                continue

            # 组合字段的 组合名称
            group_dict = relation_tags_model.get(element_model.id, {})
            group_dict.update({NodeTypeEnum.group.value: element_model})
            relation_tags_model.update({element_model.id: group_dict})

        return rule_tags_model, relation_tags_model

    @staticmethod
    def is_rule_tags(entity):
        """
        是不是实体字段

        """
        if entity.node_type == NodeTypeEnum.tag.value and entity.parent_id == '[]':
            return True

        return False

    @staticmethod
    def is_relation_tags_child(entity):
        """
        是不是组合字段的实体

        """
        if entity.node_type == NodeTypeEnum.tag.value and entity.parent_id != '[]':
            return True

        return False


    def get_file_info_and_extract_data(self, extract_id):
        """
        获取文件信息 和 抽取结果

        :param extract_id: extract_id list

        """

        down_file_obj = DownFileModel.get_by_extract_id(extract_id=extract_id)

        # 文件信息不存在，则不获取抽取数据
        if not down_file_obj:
            logger.info("get_file_info_and_extract_data 文件信息不存在")
            raise ValueError("get_file_info_and_extract_data 文件信息不存在")

        header = get_idps_header(self.idps_token)
        extract_result = requests.get(idps_extract_result_url.format(extract_id=extract_id), headers=header)

        # # 增加文件信息
        # # 临时公告不需要
        # file_info_rule_extract = FileInfoExtractData(file_info=down_file_obj, extract_data=[])
        # file_info_relation_extract = FileInfoExtractData(file_info=down_file_obj, extract_data=[])

        if extract_result.status_code == 200:
            extract_result_obj = extract_result.json()

            # 规则抽取结果
            rule_extract_result = extract_result_obj.get('item').get('result').get('tag_list')
            # 关系抽取结果
            relation_extract_result = extract_result_obj.get('item').get('result').get('relation_extract')

            # 增加 pdf_path
            model_dict = down_file_obj.__dict__
            model_dict["pdf_path"] = extract_result_obj['item']['result']['pdf_path']

            # 增加抽取结果
            # # 临时公告不需要
            # file_info_rule_extract.extract_data.extend(rule_extract_result)
            # file_info_relation_extract.extract_data.extend(relation_extract_result)
        else:
            logger.info("get_file_info_and_extract_data %s" % extract_result.content)
            raise ValueError("get_file_info_and_extract_data 获取抽取信息失败")

        return down_file_obj, rule_extract_result, relation_extract_result

    def dispose_rule_extract(self, rule_extract):

        result_list = {}

        for element_extract in rule_extract:

            if element_extract['tag_id'] not in self.rule_tags_model.keys():
                continue

            result_data = self.get_locations_chars(extract_data=element_extract)
            result_list[element_extract['tag_name']] = result_data

        self.get_empty_rule_data(result_list)
        return result_list


    @staticmethod
    def get_locations_chars(extract_data=None):
      """
      huoqu
      """

      if not extract_data or extract_data.get("after_treatment", "") == "":
        return {
          "locations": [
            {
              "bboxes": "[]",
              "page_no": -1,
              "page_size": "[]"
            }
          ],
          "chars": ""
        }

      after_treatment_dict = json.loads(extract_data.get("after_treatment"))

      return {
        "locations": after_treatment_dict["locations"],
        "chars": after_treatment_dict["data"],
      }

    def get_empty_rule_data(self, data_list):
      """
      得到得应类型的空事件组

      """

      for rule_tag_id, rule_tag in self.rule_tags_model.items():
        if rule_tag.name not in data_list.keys():
          data_list[rule_tag.name] = self.get_locations_chars()


    def dispose_relation_extract(self, relation_extract):

        result_list = {}

        # 遍历组合字段组
        for element_extract in relation_extract:

            tags_list = self.relation_tags_model[element_extract['id']][NodeTypeEnum.tag.value]
            result_list[element_extract['name']] = []

            # 遍历组合字段的每一条记录（包含若干实体字段）
            for children_group in element_extract['children']:
                group_data = {}

                for children_element in children_group["children"]:
                    children_element_dict = self.get_locations_chars_relation(children_element['value'])
                    group_data[children_element['name']] = children_element_dict

                # 处理完一条记录，需要根据 tags_list ，补全模型
                self.completion_model(tags_list, group_data)
                result_list[element_extract['name']].append(group_data)

        # 补全组合字段
        self.get_empty_relation_data(result_list)
        return result_list

    def get_locations_chars_relation(self, extract_data_list=None):
      """
      huoqu
      """

      if not extract_data_list or len(extract_data_list) == 0:
        return {
          "locations": [
            {
              "bboxes": "[]",
              "page_no": -1,
              "page_size": "[]"
            }
          ],
          "chars": ""
        }

      result_data = {
          "locations": [
          ],
          "chars": ""
        }

      for extract_data in extract_data_list:
          chars, locations = self.get_locations_chars(extract_data)["chars"], self.get_locations_chars(extract_data)["locations"]
          result_data["locations"].extend(locations)
          result_data["chars"] += (","+ chars)

      result_data["chars"] = result_data["chars"][1:]
      return result_data

    def completion_model(self, tags_list, group_data):
        """
        根据tags_list，补全一条记录
        主要针对模型抽取中，为空值的字段
        """

        for tag in tags_list:
            if tag.name not in group_data.keys():
                group_data[tag.name] = self.get_locations_chars()

    def get_empty_relation_data(self, data_list):
      """
      得到得应类型的空事件组

      """

      for relation_tags in self.relation_tags_model.values():

        if relation_tags[NodeTypeEnum.group.value].name not in data_list.keys():
            group_data = {}

            self.completion_model(relation_tags[NodeTypeEnum.tag.value], group_data)
            data_list[relation_tags[NodeTypeEnum.group.value].name] = [group_data]

