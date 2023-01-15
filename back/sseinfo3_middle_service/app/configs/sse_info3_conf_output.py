# coding=utf-8
"""
@FileName：sse_info3_conf_output
@ProjectName：
@CreateTime：2022/4/29 上午9:50
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""

from enum import IntEnum

from configs.sse_info3_tags_id import diff_info_issuer_info, diff_info_issuer_intmd, diff_info_release_profile, \
    diff_table_five_cust_sell, diff_table_five_supplier_buy, diff_if_cash_dominate, diff_if_compete, \
    diff_txt_issue_info, diff_info_point_core_prod_ratio, diff_info_core_prod_ratio_rpt_date, \
    diff_info_core_prod_ratio_item_name, diff_info_core_prod_ratio_core_prod_amt, \
    diff_info_core_prod_ratio_main_biz_amt, diff_info_core_prod_ratio_core_prod_ratio, \
    diff_info_core_prod_ratio_item_amt, diff_info_core_prod_ratio_unit, diff_info_core_prod_ratio_curr

file_version_dict = {
    "1": "申报稿"      # FileVersionEnum.one
    , "2": "上会稿"    # FileVersionEnum.two
    , "3": "注册稿"    # FileVersionEnum.three
    , "4": "其他"     # FileVersionEnum.four
}


class TypeTIdRelationEnum(IntEnum):
    """
        类型 tag_id 关系映射
    """

    # table_release_profile = 296  # 本次发行概况表格
    table_issuer_info = 299  # 发行人基本情况表格
    table_issuer_intmd = 300  # 本次发行的有关中介机构表格
    graph_equity_structure = 297  # 发行人股权结构图
    # txt_select_specific_listing_criteria = 298  # 发行人选择的上市标准情况原文
    # txt_cap_raised_usage = 301  # 募集资金用途原文
    # txt_risk_fctr= 302  # 风险因素原文
    # txt_ltd_com_setup = 303  # 有限公司设立情况、股份公司设立情况原文
    txt_issuer_setup = 304  # 有限公司设立情况、股份公司设立情况二级标题下原文
    txt_other_mkt_list = 305  # 发行人在其他证券市场的上市&挂牌情况原文
    txt_main_shdr = 306  # 发行人主要股东和实际控制人情况原文
    txt_issue_shr = 307  # 本次发行前后股本情况原文
    txt_shdr_rela = 308  # 本次发行前各股东间的关联关系及关联股东的持股比例原文
    txt_cstdn_family = 309  # 董事、监事、高级管理人员及核心技术人员之间存在的亲属关系原文
    txt_lawsuit = 310  # 董事、监事、高级管理人员及核心技术人员所持股份的质押、冻结原文
    txt_cstdn_chg = 311  # 董监高核心技术人员近两年变动情况原文
    txt_sip = 312  # 发行前发行人的股权激励及相关安排原文
    txt_agree_fulfil = 313  # 发行人与董监高核心技术人员的协议及履行情况原文
    txt_core_prod_ratio = 329 # 314  # 核心技术情况原文
    # txt_main_biz = 315  # 公司主营业务、主要产品及服务原文
    # txt_main_oprn_mode = 316  # 公司主要经营模式原文
    # txt_belong_ind = 317  # 所属行业及确定所属行业的依据、行业主管部门和管理体制、行业主要法律法规和政策情况原文
    txt_frn_oprn = 318  # 境外经营情况原文
    txt_agree_ctrl = 319  # 发行人协议控制架构情况原文
    txt_cash_dominate = 320  # 发行人报告期内资金占用和对外担保情况原文
    txt_issuer_independent = 321  # 发行人独立性情况原文-资产完整
    txt_compete = 322  # 同业竞争情况原文
    txt_ltd_com_setup = 323  # 发行人基本情况-有限公司设立情况
    txt_shr_ltd_com_setup = 324  # 发行人基本情况-股份有限公司设立情况
    txt_issuer_independent_person = 325  # 发行人独立性情况原文-人员独立
    txt_issuer_independent_money = 326  # 发行人独立性情况原文-财务独立
    txt_issuer_independent_organization = 327  # 发行人独立性情况原文-机构独立
    txt_issuer_independent_business = 328  # 发行人独立性情况原文-业务独立
    txt_core_technolo_revenue_ratio = 314 #329	 # 核心技术占收入比例情况原文
    # txt_company_main_business = 330	 # 公司主营业务原文
    # txt_company_main_product = 331	 # 公司主要产品原文
    # txt_industry_organizers = 332	 # 行业主办部门及监管体制原文
    # txt_industry_main_law = 333	 # 行业主要法律法规政策原文

    # 信息点
    info_point_issue_shr = 252 # 本次发行前后股本情况
    ipis_num = 253 # 本次发行前后股本情况-本次拟发行人民币普通股数量
    ipis_total_num = 254 # 本次发行前后股本情况-发行后公司的总股本
    ipis_name = 255 # 本次发行前后股本情况-股东名称
    ipis_pre_num = 256 # 本次发行前后股本情况-发行前持股数量
    ipis_after_num = 257 # 本次发行前后股本情况-发行后持股数量
    ipis_pre_ratio = 258 # 本次发行前后股本情况-发行前持股比例
    ipis_after_ratio = 259 # 本次发行前后股本情况-发行后持股比例
    ipis_unit = 260 # 本次发行前后股本情况-股本单位
    ipis_pre_total_num = 287 # 本次发行前后股本情况-发行前公司的总股本

    info_point_cstdn_part_time = 246    # 董监高及核心技术人员兼职情况
    ipcpt_name = 247    # 人员姓名
    ipcpt_company_office = 248  # 公司职务
    ipcpt_part_time_company = 249   # 兼职单位
    ipcpt_part_time_job = 250   # 兼职职务
    ipcpt_correlation = 251 # 与公司的关联关系

    info_point_five_cust_sell = 261 	# 五大客户销售金额及占比情况
    ipfcs_company_name = 262 	# 五大客户销售金额及占比情况-公司名称
    ipfcs_num = 263 	# 五大客户销售金额及占比情况-序号
    ipfcs_name = 264 	# 五大客户销售金额及占比情况-客户名称
    ipfcs_type = 265 	# 五大客户销售金额及占比情况-销售产品/类型
    ipfcs_amount = 266 	# 五大客户销售金额及占比情况-销售金额
    ipfcs_ratio = 267 	# 五大客户销售金额及占比情况-占营业收入的比例
    ipfcs_unit = 268 	# 五大客户销售金额及占比情况-单位
    ipfcs_currency = 269 	# 五大客户销售金额及占比情况-币种
    ipfcs_reporting_period = 293 	# 五大客户销售金额及占比情况-报告期
    ipfcs_business_line = 294 	# 五大客户销售金额及占比情况-业务线名称

    info_point_five_supplier_buy = 270  # 五大供应商采购金额及占比情况
    ipfsb_reporting_period = 271  # 五大供应商采购金额及占比情况-报告期
    ipfsb_company_name = 272  # 五大供应商采购金额及占比情况-公司名称
    ipfsb_num = 273  # 五大供应商采购金额及占比情况-序号
    ipfsb_name = 274  # 五大供应商采购金额及占比情况-供应商名称
    ipfsb_type = 275  # 五大供应商采购金额及占比情况-采购产品类型
    ipfsb_amount = 276  # 五大供应商采购金额及占比情况-采购金额
    ipfsb_ratio = 277  # 五大供应商采购金额及占比情况-占采购总额的比例
    ipfsb_unit = 278  # 五大供应商采购金额及占比情况-单位
    ipfsb_currency = 279  # 五大供应商采购金额及占比情况-币种
    ipfsb_business_line = 295  # 五大供应商采购金额及占比情况-业务线名称

    info_point_fin_fare = 280  # 财务费用
    ipff_reporting_period = 281  # 财务费用-报告期
    ipff_name = 282  # 财务费用-财务费用项目名称
    ipff_amount = 283  # 财务费用-财务费用金额
    ipff_ratio = 284  # 财务费用-财务费用占比
    ipff_unit = 285  # 财务费用-单位
    ipff_currency = 286  # 财务费用-币种

    info_point_cstdn_invest = 288  # 董监高及核心技术人员的其他对外投资情况
    ipci_name = 289  # 董监高及核心技术人员的其他对外投资情况-人员姓名
    ipci_company_office = 290  # 董监高及核心技术人员的其他对外投资情况-公司职务
    ipci_investee_company = 291  # 董监高及核心技术人员的其他对外投资情况-被投资公司/企业
    ipci_ratio = 292  # 董监高及核心技术人员的其他对外投资情况-持股比例/出资比例

    info_issuer_info = diff_info_issuer_info or 338  # 发行人基本情况-信息点
    info_issuer_intmd = diff_info_issuer_intmd or 339  # 本次发行的有关中介机构-信息点
    info_release_profile = diff_info_release_profile or 340  # 本次发行概况-信息点

    table_five_cust_sell = diff_table_five_cust_sell or 336 # 业务和技术-报告期内各期向前五大客户销售金额及占比情况（表格）
    table_five_supplier_buy = diff_table_five_supplier_buy or 337 # 业务和技术-报告期内向前五大供应商采购金额及占比情况（表格）

    if_cash_dominate = diff_if_cash_dominate or 341  # 资金占用和对外担保情况-判断'
    if_compete = diff_if_compete or 342  # 同业竞争情况-判断
    txt_issue_info = diff_txt_issue_info or 366  # 本次发行概况-原文

    info_point_core_prod_ratio = diff_info_point_core_prod_ratio or 887  # 核心技术收入占主营收入比例
    info_core_prod_ratio_rpt_date = diff_info_core_prod_ratio_rpt_date or 888  # 报告期
    info_core_prod_ratio_item_name = diff_info_core_prod_ratio_item_name or 889  # 项目名称
    info_core_prod_ratio_core_prod_amt = diff_info_core_prod_ratio_core_prod_amt or 890  # 核心技术产品收入
    info_core_prod_ratio_main_biz_amt = diff_info_core_prod_ratio_main_biz_amt or 891  # 主营业务收入
    info_core_prod_ratio_core_prod_ratio = diff_info_core_prod_ratio_core_prod_ratio or 892  # 核心技术产品收入占主营业务收入比例
    info_core_prod_ratio_item_amt = diff_info_core_prod_ratio_item_amt or 893  # 项目金额
    info_core_prod_ratio_unit = diff_info_core_prod_ratio_unit or 894  # 单位
    info_core_prod_ratio_curr = diff_info_core_prod_ratio_curr or 895  # 币种

schema_name_dict = {

    # TypeTIdRelationEnum.table_release_profile: {
    #     "schema_name": "Issue_Info_Txt_V1.0"
    #     , "type_code": "001099020020"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # },
    TypeTIdRelationEnum.graph_equity_structure: {
        "schema_name": "Eqty_Struc_Pic_V1.0"
        , "type_code": "002000"
        , "type": "科创板招股书图片表"
        , "graph_type_code": "1"
        , "graph_type": "股权结构图"
        , "parse_first": False
        , "parse_second": False
    }
    # , TypeTIdRelationEnum.txt_select_specific_listing_criteria: {
    #     "schema_name": "Issuer_List_Stde_Txt_V1.0"
    #     , "type_code": "001099020040"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    , TypeTIdRelationEnum.table_issuer_info: {
        "schema_name": "Issuer_Info_Table_V1.0"
        , "type_code": "001099020000"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "020000"
        , "txt_type": "概览-发行人基本情况（表格）"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.table_issuer_intmd: {
        "schema_name": "Issue_Intmd_Table_V1.0"
        , "type_code": "001099020010"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "020010"
        , "txt_type": "概览-本次发行的有关中介机构（表格）"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.table_five_cust_sell: {
        "schema_name": "Five_Cust_Sell_Table_V1.0"
        , "type_code": "001099060090"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "060090"
        , "txt_type": "业务和技术-报告期内各期向前五大客户销售金额及占比情况（表格）"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.table_five_supplier_buy: {
        "schema_name": "Five_Supplier_Buy_Table_V1.0"
        , "type_code": "001099060100"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "060100"
        , "txt_type": "业务和技术-报告期内向前五大供应商采购金额及占比情况（表格）"
        , "parse_first": False
        , "parse_second": False
    }

    # , TypeTIdRelationEnum.txt_cap_raised_usage: {
    #     "schema_name": "Cap_Raised_Usage_Txt_V1.0"
    #     , "type_code": "001099020060"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    # , TypeTIdRelationEnum.txt_risk_fctr: {
    #     "schema_name": "Risk_Fctr_Txt_V1.0"
    #     , "type_code": "001099040000"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": True
    # }
    , TypeTIdRelationEnum.txt_ltd_com_setup: {
        "schema_name": "Ltd_Com_Setup_Txt_V1.0"
        , "type_code": "001099050000"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050000"
        , "txt_type": "发行人基本情况-有限公司设立情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_shr_ltd_com_setup: {
        "schema_name": "Shr_Ltd_Com_Setup_Txt_V1.0"
        , "type_code": "001099050001"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050001"
        , "txt_type": "发行人基本情况-股份有限公司设立情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issuer_setup: {
        "schema_name": "Issuer_Setup_Txt_V1.0"
        , "type_code": "001099050010"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050010"
        , "txt_type": "发行人基本情况-发行人设立情况"
        , "parse_first": True
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_other_mkt_list: {
        "schema_name": "Other_Mkt_List_Txt_V1.0"
        , "type_code": "001099050020"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050020"
        , "txt_type": "发行人基本情况-发行人在其他证券市场的上市/挂牌情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_main_shdr: {
        "schema_name": "Main_Shdr_Txt_V1.0"
        , "type_code": "001099050030"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050030"
        , "txt_type": "发行人基本情况-发行人控股股东、实际控制人及持有发行人 5%以上股份的主要股东基本情况（整个小节）"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issue_shr: {
        "schema_name": "Issue_Shr_Txt_V1.0"
        , "type_code": "001099050040"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050040"
        , "txt_type": "发行人基本情况-本次发行前后股本情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_shdr_rela: {
        "schema_name": "Shdr_Rela_Txt_V1.0"
        , "type_code": "001099050050"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050050"
        , "txt_type": "发行人基本情况-本次发行前各股东间的关联关系情况说明"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_cstdn_family: {
        "schema_name": "Cstdn_Family_Txt_V1.0"
        , "type_code": "001099050060"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050060"
        , "txt_type": "发行人基本情况-董事、监事、高级管理人员及核心技术人员之间存在的亲属关系"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_lawsuit: {
        "schema_name": "Lawsuit_Txt_V1.0"
        , "type_code": "001099050080"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050080"
        , "txt_type": "发行人基本情况-质押、冻结或发生诉讼纠纷的情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_cstdn_chg: {
        "schema_name": "Cstdn_Chg_Txt_V1.0"
        , "type_code": "001099050090"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050090"
        , "txt_type": "发行人基本情况-董监高核心技术人员近两年变动情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_sip: {
        "schema_name": "SIP_Txt_V1.0"
        , "type_code": "001099050100"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050100"
        , "txt_type": "发行人基本情况-股权激励及员工持股计划情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_agree_fulfil: {
        "schema_name": "Agree_Fulfil_Txt_V1.0"
        , "type_code": "001099050070"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "050070"
        , "txt_type": "发行人基本情况-发行人与董监高核心技术人员的协议及履行情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_core_prod_ratio: {
        "schema_name": "Core_Prod_Ratio_Txt_V1.0"
        , "type_code": "001099060110"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "060110"
        , "txt_type": "业务和技术-发行人核心技术产品收入占主营业务收入的比例"
        , "parse_first": False
        , "parse_second": False
    }
    # , TypeTIdRelationEnum.txt_main_biz: {
    #     "schema_name": "Main_Biz_Txt_V1.0"
    #     , "type_code": "001099060000"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    # , TypeTIdRelationEnum.txt_main_oprn_mode: {
    #     "schema_name": "Main_Oprn_Mode_Txt_V1.0"
    #     , "type_code": "001099060030"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": True
    #     , "parse_second": False
    # }
    # , TypeTIdRelationEnum.txt_belong_ind: {
    #     "schema_name": "Belong_Ind_Txt_V1.0"
    #     , "type_code": "001099060050"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    , TypeTIdRelationEnum.txt_frn_oprn: {
        "schema_name": "Frn_Oprn_Txt_V1.0"
        , "type_code": "001099060120"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "060120"
        , "txt_type": "业务和技术-境外经营情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_agree_ctrl: {
        "schema_name": "Agree_Ctrl_Txt_V1.0"
        , "type_code": "001099070000"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070000"
        , "txt_type": "公司治理与独立性-发行人协议控制架构情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_cash_dominate: {
        "schema_name": "Cash_Dominate_Txt_V1.0"
        , "type_code": "001099070010"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070010"
        , "txt_type": "公司治理与独立性-资金占用情况和对外担保情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issuer_independent: {
        "schema_name": "Asset_Cpl_Txt_V1.0"
        , "type_code": "001099070020"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070020"
        , "txt_type": "公司治理与独立性-资产完整情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_compete: {
        "schema_name": "Compete_Txt_V1.0"
        , "type_code": "001099070070"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070070"
        , "txt_type": "公司治理与独立性-同业竞争情况"
        , "parse_first": True
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issuer_independent_person: {
        "schema_name": "Emp_Independent_Txt_V1.0"
        , "type_code": "001099070030"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070030"
        , "txt_type": "公司治理与独立性-人员独立情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issuer_independent_money: {
        "schema_name": "Fin_Independent_Txt_V1.0"
        , "type_code": "001099070040"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070040"
        , "txt_type": "公司治理与独立性-财务独立方面"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issuer_independent_organization: {
        "schema_name": "Inst_Independent_Txt_V1.0"
        , "type_code": "001099070050"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070050"
        , "txt_type": "公司治理与独立性-机构独立方面"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issuer_independent_business: {
        "schema_name": "Biz_Independent_Txt_V1.0"
        , "type_code": "001099070060"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "070060"
        , "txt_type": "公司治理与独立性-业务独立方面"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_core_technolo_revenue_ratio: {
        "schema_name": "Core_Tech_Txt_V1.0"
        , "type_code": "001099060111"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "060111"
        , "txt_type": "业务和技术-发行人核心技术情况"
        , "parse_first": False
        , "parse_second": False
    }
    # , TypeTIdRelationEnum.txt_company_main_business: {
    #     "schema_name": "Main_Biz_Txt_V1.0"
    #     , "type_code": "001099060000"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    # , TypeTIdRelationEnum.txt_company_main_product: {
    #     "schema_name": "Main_Prod_Txt_V1.0"
    #     , "type_code": "001099060010"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    # , TypeTIdRelationEnum.txt_industry_organizers: {
    #     "schema_name": "Ind_Supvs_Txt_V1.0"
    #     , "type_code": "001099060060"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }
    # , TypeTIdRelationEnum.txt_industry_main_law: {
    #     "schema_name": "Ind_Law_Txt_V1.0"
    #     , "type_code": "001099060070"
    #     , "type": "科创板招股书原文信息表"
    #     , "parse_first": False
    #     , "parse_second": False
    # }

    # 信息点
    , TypeTIdRelationEnum.info_point_issue_shr: {
        "schema_name": "Issue_Shr_V1.0"
        , "type_code": "003000"
        , "type": "科创板招股书发行前后股本情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_point_cstdn_part_time: {
        "schema_name": "Cstdn_Part_Time_V1.0"
        , "type_code": "004000"
        , "type": "科创板招股书董监高兼职情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_point_cstdn_invest: {
        "schema_name": "Cstdn_Invest_V1.0"
        , "type_code": "005000"
        , "type": "科创板招股书董监高对外投资情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_point_five_cust_sell: {
        "schema_name": "Five_Cust_Sell_V1.0"
        , "type_code": "006000"
        , "type": "科创板招股书前五客户销售情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_point_five_supplier_buy: {
        "schema_name": "Five_Supplier_Buy_V1.0"
        , "type_code": "007000"
        , "type": "科创板招股书前五供应商采购情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_point_fin_fare: {
        "schema_name": "Fin_Fare_V1.0"
        , "type_code": "009000"
        , "type": "科创板招股书财务状况分析表"
        , "parse_first": False
        , "parse_second": False
    }

    , TypeTIdRelationEnum.info_issuer_info: {
        "schema_name": "Issuer_Info__V1.0"
        , "type_code": "001100"
        , "type": "科创板招股书发行人基本情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_issuer_intmd: {
        "schema_name": "Issue_Intmd_V1.0"
        , "type_code": "001200"
        , "type": "科创板招股书中介机构基本情况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_release_profile: {
        "schema_name": "Issue_Info_V1.0"
        , "type_code": "001300"
        , "type": "科创板招股书发行概况表"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.if_cash_dominate: {
        "schema_name": "Cash_Dominate_IF_V1.0"
        , "type_code": "008099070010"
        , "type": "科创板招股书判断信息表"
        , "if_type_code": "070010"
        , "if_type": "公司治理与独立性-资金占用情况和对外担保情况-是否存在资金占用情况和对外担保情况"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.if_compete: {
        "schema_name": "Compete_IF_V1.0"
        , "type_code": "008099070070"
        , "type": "科创板招股书判断信息表"
        , "if_type_code": "070070"
        , "if_type": "公司治理与独立性-同业竞争情况-是否存在同业竞争"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.txt_issue_info: {
        "schema_name": "Issue_Info_Txt_V1.0"
        , "type_code": "001099020020"
        , "type": "科创板招股书原文信息表"
        , "txt_type_code": "020020"
        , "txt_type": "概览-本次发行概况（表格）"
        , "parse_first": False
        , "parse_second": False
    }
    , TypeTIdRelationEnum.info_point_core_prod_ratio: {
        "schema_name": "Core_Prod_Ratio_V1.0"
        , "type_code": "007100"
        , "type": "科创板招股书核心技术产品占比"
        , "parse_first": False
        , "parse_second": False
    }

}

"""
原文类 在规则抽取结果中
"""
# 原文
type_txt = {"sheet_name": "原文信息表"
    , "tag_id": [
        # TypeTIdRelationEnum.txt_select_specific_listing_criteria,
        TypeTIdRelationEnum.table_issuer_info
        , TypeTIdRelationEnum.table_issuer_intmd
        # , TypeTIdRelationEnum.table_release_profile
        , TypeTIdRelationEnum.txt_issue_info
        # , TypeTIdRelationEnum.txt_cap_raised_usage
        # , TypeTIdRelationEnum.txt_risk_fctr
        , TypeTIdRelationEnum.txt_ltd_com_setup
        , TypeTIdRelationEnum.txt_shr_ltd_com_setup
        , TypeTIdRelationEnum.txt_issuer_setup
        , TypeTIdRelationEnum.txt_other_mkt_list
        , TypeTIdRelationEnum.txt_main_shdr
        , TypeTIdRelationEnum.txt_issue_shr
        , TypeTIdRelationEnum.txt_shdr_rela
        , TypeTIdRelationEnum.txt_cstdn_family
        , TypeTIdRelationEnum.txt_lawsuit
        , TypeTIdRelationEnum.txt_cstdn_chg
        , TypeTIdRelationEnum.txt_sip
        , TypeTIdRelationEnum.txt_agree_fulfil
        , TypeTIdRelationEnum.txt_core_prod_ratio
        # , TypeTIdRelationEnum.txt_main_oprn_mode
        # , TypeTIdRelationEnum.txt_belong_ind
        , TypeTIdRelationEnum.txt_frn_oprn
        , TypeTIdRelationEnum.txt_agree_ctrl
        , TypeTIdRelationEnum.txt_cash_dominate
        , TypeTIdRelationEnum.txt_issuer_independent
        , TypeTIdRelationEnum.txt_compete
        , TypeTIdRelationEnum.txt_issuer_independent_person
        , TypeTIdRelationEnum.txt_issuer_independent_money
        , TypeTIdRelationEnum.txt_issuer_independent_organization
        , TypeTIdRelationEnum.txt_issuer_independent_business
        , TypeTIdRelationEnum.txt_core_technolo_revenue_ratio
        # , TypeTIdRelationEnum.txt_company_main_business
        # , TypeTIdRelationEnum.txt_company_main_product
        # , TypeTIdRelationEnum.txt_industry_organizers
        # , TypeTIdRelationEnum.txt_industry_main_law
        , TypeTIdRelationEnum.table_five_cust_sell
        , TypeTIdRelationEnum.table_five_supplier_buy
    ]}

# 图片
type_graph = {"sheet_name": "图片表", "tag_id": [TypeTIdRelationEnum.graph_equity_structure]}

# 原文类 表格kv形式
info_issuer_info = {"sheet_name": "发行人基本情况表"
    , "tag_id": [
        TypeTIdRelationEnum.info_issuer_info
    ]
                         }

info_issuer_intmd = {"sheet_name": "中介机构基本情况表"
    , "tag_id": [
        TypeTIdRelationEnum.info_issuer_intmd
    ]
                          }

info_release_profile = {"sheet_name": "发行概况表"
    , "tag_id": [
        TypeTIdRelationEnum.info_release_profile
    ]
                             }
# 原文类 判断
if_table = {"sheet_name": "判断信息表"
    , "tag_id": [
        TypeTIdRelationEnum.if_cash_dominate,
        TypeTIdRelationEnum.if_compete
    ]
                 }

"""
信息点类 在关系抽取结果中
"""
# 信息点
info_point_issue_shr = {"sheet_name": "股本情况表"
    , "tag_id": [
        TypeTIdRelationEnum.ipis_num  # 本次发行前后股本情况-本次拟发行人民币普通股数量
        , TypeTIdRelationEnum.ipis_total_num  # 本次发行前后股本情况-发行后公司的总股本
        , TypeTIdRelationEnum.ipis_name  # 本次发行前后股本情况-股东名称
        , TypeTIdRelationEnum.ipis_pre_num  # 本次发行前后股本情况-发行前持股数量
        , TypeTIdRelationEnum.ipis_after_num  # 本次发行前后股本情况-发行后持股数量
        , TypeTIdRelationEnum.ipis_pre_ratio  # 本次发行前后股本情况-发行前持股比例
        , TypeTIdRelationEnum.ipis_after_ratio  # 本次发行前后股本情况-发行后持股比例
        , TypeTIdRelationEnum.ipis_unit  # 本次发行前后股本情况-股本单位
        , TypeTIdRelationEnum.ipis_pre_total_num  # 本次发行前后股本情况-发行前公司的总股本
    ]
    , "group_id": TypeTIdRelationEnum.info_point_issue_shr}

info_point_cstdn_part_time = {"sheet_name": "兼职情况表"
    , "tag_id": [
        TypeTIdRelationEnum.ipcpt_name  # 人员姓名
        , TypeTIdRelationEnum.ipcpt_company_office  # 公司职务
        , TypeTIdRelationEnum.ipcpt_part_time_company  # 兼职单位
        , TypeTIdRelationEnum.ipcpt_part_time_job  # 兼职职务
        , TypeTIdRelationEnum.ipcpt_correlation  # 与公司的关联关系
    ]
    , "group_id": TypeTIdRelationEnum.info_point_cstdn_part_time}

info_point_cstdn_invest = {"sheet_name": "对外投资情况表"
    , "tag_id": [
        TypeTIdRelationEnum.ipci_name  # 董监高及核心技术人员的其他对外投资情况-人员姓名
        , TypeTIdRelationEnum.ipci_company_office  # 董监高及核心技术人员的其他对外投资情况-公司职务
        , TypeTIdRelationEnum.ipci_investee_company  # 董监高及核心技术人员的其他对外投资情况-被投资公司/企业
        , TypeTIdRelationEnum.ipci_ratio  # 董监高及核心技术人员的其他对外投资情况-持股比例/出资比例
    ]
    , "group_id": TypeTIdRelationEnum.info_point_cstdn_invest}

info_point_five_cust_sell = {"sheet_name": "前五客户情况表"
    , "tag_id": [
        TypeTIdRelationEnum.ipfcs_company_name  # 五大客户销售金额及占比情况-公司名称
        , TypeTIdRelationEnum.ipfcs_num  # 五大客户销售金额及占比情况-序号
        , TypeTIdRelationEnum.ipfcs_name  # 五大客户销售金额及占比情况-客户名称
        , TypeTIdRelationEnum.ipfcs_type  # 五大客户销售金额及占比情况-销售产品/类型
        , TypeTIdRelationEnum.ipfcs_amount  # 五大客户销售金额及占比情况-销售金额
        , TypeTIdRelationEnum.ipfcs_ratio  # 五大客户销售金额及占比情况-占营业收入的比例
        , TypeTIdRelationEnum.ipfcs_unit  # 五大客户销售金额及占比情况-单位
        , TypeTIdRelationEnum.ipfcs_currency  # 五大客户销售金额及占比情况-币种
        , TypeTIdRelationEnum.ipfcs_reporting_period  # 五大客户销售金额及占比情况-报告期
        , TypeTIdRelationEnum.ipfcs_business_line  # 五大客户销售金额及占比情况-业务线名称
    ]
    , "group_id": TypeTIdRelationEnum.info_point_five_cust_sell}

info_point_five_supplier_buy = {"sheet_name": "前五供应商情况表"
    , "tag_id": [
        TypeTIdRelationEnum.ipfsb_reporting_period  # 五大供应商采购金额及占比情况-报告期
        , TypeTIdRelationEnum.ipfsb_company_name  # 五大供应商采购金额及占比情况-公司名称
        , TypeTIdRelationEnum.ipfsb_num  # 五大供应商采购金额及占比情况-序号
        , TypeTIdRelationEnum.ipfsb_name  # 五大供应商采购金额及占比情况-供应商名称
        , TypeTIdRelationEnum.ipfsb_type  # 五大供应商采购金额及占比情况-采购产品类型
        , TypeTIdRelationEnum.ipfsb_amount  # 五大供应商采购金额及占比情况-采购金额
        , TypeTIdRelationEnum.ipfsb_ratio  # 五大供应商采购金额及占比情况-占采购总额的比例
        , TypeTIdRelationEnum.ipfsb_unit  # 五大供应商采购金额及占比情况-单位
        , TypeTIdRelationEnum.ipfsb_currency  # 五大供应商采购金额及占比情况-币种
    ]
    , "group_id": TypeTIdRelationEnum.info_point_five_supplier_buy}

info_point_fin_fare = {"sheet_name": "财务状况分析表"
    , "tag_id": [
        TypeTIdRelationEnum.ipff_reporting_period  # 财务费用-报告期
        , TypeTIdRelationEnum.ipff_name  # 财务费用-财务费用项目名称
        , TypeTIdRelationEnum.ipff_amount  # 财务费用-财务费用金额
        , TypeTIdRelationEnum.ipff_ratio  # 财务费用-财务费用占比
        , TypeTIdRelationEnum.ipff_unit  # 财务费用-单位
        , TypeTIdRelationEnum.ipff_currency  # 财务费用-币种
    ]
    , "group_id": TypeTIdRelationEnum.info_point_fin_fare}

info_point_core_prod_ratio = {"sheet_name": "核心技术产品占比"
    , "tag_id": [
        TypeTIdRelationEnum.info_core_prod_ratio_rpt_date
        , TypeTIdRelationEnum.info_core_prod_ratio_item_name
        , TypeTIdRelationEnum.info_core_prod_ratio_core_prod_amt
        , TypeTIdRelationEnum.info_core_prod_ratio_main_biz_amt
        , TypeTIdRelationEnum.info_core_prod_ratio_core_prod_ratio
        , TypeTIdRelationEnum.info_core_prod_ratio_item_amt
        , TypeTIdRelationEnum.info_core_prod_ratio_unit
        , TypeTIdRelationEnum.info_core_prod_ratio_curr
    ]
    , "group_id": TypeTIdRelationEnum.info_point_core_prod_ratio
                                   }

# 关系抽取的 list
relation_extract_list = [info_point_issue_shr, info_point_cstdn_part_time,
                              info_point_cstdn_invest, info_point_five_cust_sell,
                              info_point_five_supplier_buy, info_point_fin_fare,
                              info_point_core_prod_ratio, ]
# 关系抽取的 tag_id list
relation_extract_tag_id_list = [tag_id for element in relation_extract_list
                                     for tag_id in element["tag_id"]]
