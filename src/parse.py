# coding:utf-8

from pdf import PDFTools


class PDFParser(object):
    NO_INDEX = -1
    CONTENT_HEIGHT = 8.964
    TILTE_HEIGHT = 10.39824
    CONTENT_FONT = 'TDVITV+SimSun'

    def __init__(self, pdf_path):
        self.page_box = PDFTools.get_page_box(file_path=pdf_path)
        text_box_list = self.page_box.text_box_list
        self.page_box.text_box_list = PDFTools.quick_sort_text_box(
            text_box_list)
        self.text_box_list = self.page_box.text_box_list

    def get_index(self, special_text, offset=0):
        """根据特征值获得相应位置"""
        for i in range(len(self.text_box_list[offset:])):
            if special_text in self.text_box_list[i+offset].content:
                return i + offset
        return PDFParser.NO_INDEX

    def get_text_box(self, special_text, offset=0):
        """根据特征值获得相应的文本"""
        index = self.get_index(special_text,offset)
        return self.text_box_list[index]

    def get_report_infor(self):
        """获得报告信息"""
        start_index = self.get_index(u'报告编号')
        if start_index == PDFParser.NO_INDEX:
            return None
        return {
            u'报告编号': self.text_box_list[start_index].content,
            u'报告请求时间': self.text_box_list[start_index+1].content,
            u'报告时间': self.text_box_list[start_index+2].content
        }

    def get_query_infor(self):
        """获得查询信息"""
        start_index = self.get_index(u'查询原因')
        if start_index == PDFParser.NO_INDEX:
            return None
        end_index = self.get_index(u'一 个人基本信息')
        if end_index == PDFParser.NO_INDEX:
            return None
        text_box_list = PDFTools.quick_sort_text_box_base_x(
            self.text_box_list[start_index+1:end_index])
        text_box_list = PDFTools.merge_box_base_x(text_box_list)
        return {
            u'被查询者姓名': text_box_list[0].content,
            u'被查询者证件类型': text_box_list[1].content,
            u'被查询者证件号码': text_box_list[2].content,
            u'查询操作员': text_box_list[3].content,
            u'查询原因': text_box_list[4].content
        }

    def get_person(self):
        """获得身份信息"""
        start_index = self.get_index(u'身份信息')
        if start_index == PDFParser.NO_INDEX:
            return None
        end_index = self.get_index(u'配偶信息')
        if end_index == PDFParser.NO_INDEX:
            return None
        data_list = self.text_box_list[start_index:end_index]
        org_list = PDFTools.get_same_name_text_box(data_list,
                                                        u'数据发生机构名称')
        sex = PDFTools.get_same_name_text_box(data_list, u'性别')[0]
        birthday = PDFTools.get_same_name_text_box(data_list, u'出生日期')[0]
        married = PDFTools.get_same_name_text_box(data_list, u'婚姻状况')[0]
        phone = PDFTools.get_same_name_text_box(data_list, u'手机号码')[0]
        work_phone = PDFTools.get_same_name_text_box(data_list, u'单位电话')[0]
        home_phone = PDFTools.get_same_name_text_box(data_list, u'住宅电话')[0]
        education = PDFTools.get_same_name_text_box(data_list, u'学历')[0]
        degree = PDFTools.get_same_name_text_box(data_list, u'学位')[0]
        contact_addr = PDFTools.get_same_name_text_box(data_list, u'通讯地址')[0]
        home_addr = PDFTools.get_same_name_text_box(data_list, u'户籍地址')[0]
        merge_box = PDFTools.get_merge_text_box
        return {
            u'性别': merge_box(data_list, sex, org_list[0], None, birthday).content,
            u'出生日期': merge_box(data_list, birthday, org_list[1], sex, married).content,
            u'婚姻状况': merge_box(data_list, married, org_list[2], birthday, phone).content,
            u'手机号码': merge_box(data_list, phone, org_list[3], married, None).content,
            u'性别数据发生机构': merge_box(data_list, org_list[0], work_phone, None, org_list[1]).content,
            u'出生日期数据发生机构': merge_box(data_list, org_list[1], home_phone, org_list[0], org_list[2]).content,
            u'婚姻状况数据发生机构': merge_box(data_list, org_list[2], education, org_list[1], org_list[3]).content,
            u'手机号码数据发生机构': merge_box(data_list, org_list[3], degree, org_list[2], None).content,
            u'单位电话': merge_box(data_list, work_phone, org_list[4], None, home_phone).content,
            u'住宅电话': merge_box(data_list, home_phone, org_list[5], work_phone, education).content,
            u'学历':  merge_box(data_list, education, org_list[6], home_phone, degree).content,
            u'学位': merge_box(data_list, degree, org_list[7], education, None).content,
            u'单位电话数据发生机构': merge_box(data_list, org_list[4], contact_addr, None, org_list[5]).content,
            u'住宅电话数据发生机构': merge_box(data_list, org_list[5], contact_addr, org_list[4], org_list[6]).content,
            u'学历数据发生机构': merge_box(data_list, org_list[6], home_addr, org_list[5], org_list[7]).content,
            u'学位电话数据发生机构': merge_box(data_list, org_list[7], home_addr, org_list[6], None).content,
            u'通讯地址': merge_box(data_list, contact_addr, org_list[8], None, home_addr).content,
            u'户籍地址': merge_box(data_list, home_addr, org_list[9], contact_addr, None).content,
            u'通讯地址数据发生机构': merge_box(data_list, org_list[8], None, None, org_list[9]).content,
            u'户籍地址数据发生机构': merge_box(data_list, org_list[9], None, org_list[8], None).content,
        }

    def get_couple(self):
        """获得配偶信息"""
        start_index = self.get_index(u'配偶信息')
        if start_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1)
        return {
            u'姓名': data_list[0].content,
            u'证件类型': data_list[1].content,
            u'证件号码': data_list[2].content,
            u'工作单位': data_list[3].content,
            u'联系电话': data_list[4].content,
            u'数据发生机构': data_list[5].content
        }

    def get_living(self):
        """获得居住信息"""
        start_index = self.get_index(u'居住信息')
        if start_index == PDFParser.NO_INDEX:
            return None
        end_index = self.get_index(u'职业信息')
        if end_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:end_index]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1)
        number_list = PDFTools.get_same_name_text_box(text_box_list, u'编号')
        address = PDFTools.get_same_name_text_box(text_box_list, u'居住地址')[0]
        status = PDFTools.get_same_name_text_box(text_box_list, u'居住状况')[0]
        org = PDFTools.get_same_name_text_box(text_box_list, u'数据发生机构名称')[0]
        update_date = PDFTools.get_same_name_text_box(text_box_list,
                                                      u'信息更新')[0]

        firsts_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number_list[0], number_list[1], None, address)
        second_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number_list[1], None, None, org)
        merge_box = PDFTools.get_merge_text_box
        livings = list()
        for i in range(len(firsts_numbers)):
            if i == 0:
                up = number_list[0]
                up2 = number_list[1]
            else:
                up = firsts_numbers[i-1]
                up2 = second_numbers[i-1]
            if i == len(firsts_numbers) - 1:
                bottom = number_list[1]
                bottom2 = None
            else:
                bottom = firsts_numbers[i+1]
                bottom2 = second_numbers[i+1]
            living = {
                u'编号': firsts_numbers[i].content,
                u'居住地址': merge_box(data_list, up, bottom, firsts_numbers[i],
                                   status).content,
                u'居住状况': merge_box(data_list, up, bottom, address,
                                   update_date).content,
                u'信息更新日期': merge_box(data_list, up, bottom, status,
                                   None).content,
                u'数据发生机构名称': merge_box(data_list, up2, bottom2,
                                       number_list[1], None).content
            }
            livings.append(living)
        return livings

    def get_works(self):
        """获得职业信息"""
        start_index = self.get_index(u'职业信息')
        if start_index == PDFParser.NO_INDEX:
            return None
        end_index = self.get_index(u'二 信息概要')
        if end_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index+1:end_index]
        data_list = PDFTools.filter_by_font(text_box_list, PDFParser.CONTENT_FONT)
        number_list = PDFTools.get_same_name_text_box(text_box_list, u'编号')
        company = PDFTools.get_same_name_text_box(text_box_list, u'工作单位')[0]
        address = PDFTools.get_same_name_text_box(text_box_list, u'单位地址')[0]
        job = PDFTools.get_same_name_text_box(text_box_list, u'职业')[0]
        job_work = PDFTools.get_same_name_text_box(text_box_list, u'职务')[0]
        industry = PDFTools.get_same_name_text_box(text_box_list, u'行业')[0]
        title = PDFTools.get_same_name_text_box(text_box_list, u'职称')[0]
        import_year = PDFTools.get_same_name_text_box(text_box_list,
                                                      u'进入本单位')[0]
        org = PDFTools.get_same_name_text_box(text_box_list, u'数据发生机构名称')[0]
        update_date = PDFTools.get_same_name_text_box(text_box_list,
                                                      u'信息更新')[0]
        firsts_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number_list[0], number_list[1], None, company)
        second_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number_list[1], number_list[2], None, job)
        third_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number_list[2], None, None, org)
        merge_box = PDFTools.get_merge_text_box
        works = list()
        for i in range(len(firsts_numbers)):
            if i == 0:
                up = number_list[0]
                up2 = number_list[1]
                up3 = number_list[2]
            else:
                up = firsts_numbers[i-1]
                up2 = second_numbers[i-1]
                up3 = third_numbers[i-1]
            if i == len(firsts_numbers) - 1:
                bottom = number_list[1]
                bottom2 = number_list[2]
                bottom3 = None
            else:
                bottom = firsts_numbers[i+1]
                bottom2 = second_numbers[i+1]
                bottom3 = third_numbers[i+1]
            work = {
                u'编号': firsts_numbers[i].content,
                u'工作单位': merge_box(data_list, up, bottom, firsts_numbers[i],
                                   address).content,
                u'单位地址': merge_box(data_list, up, bottom, company,
                                   None).content,
                u'职业': merge_box(data_list, up2, bottom2, second_numbers[i],
                                     industry).content,
                u'行业': merge_box(data_list, up2, bottom2,
                                       job, job_work ).content,
                u'职务': merge_box(data_list, up2, bottom2, industry,
                                 title).content,
                u'职称': merge_box(data_list, up2, bottom2, job_work,
                                 import_year).content,
                u'进入本单位年份': merge_box(data_list, up2, bottom2,
                                 title, update_date).content,
                u'信息更新日期': merge_box(data_list, up2, bottom2,
                                 import_year, None).content,
                u'数据发生机构名称': merge_box(data_list, up3, bottom3,
                                 number_list[2], None).content
            }
            works.append(work)
        return works

    def get_credit_tips(self):
        """获得信用提示"""
        start_index = self.get_index(u'信用提示')
        if start_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1, number=10)
        return {
            u'个人住房贷款笔数': data_list[0].content,
            u'个人商用房（包括商住两用）贷款笔数': data_list[1].content,
            u'其他贷款笔数': data_list[2].content,
            u'首笔贷款发放月份': data_list[3].content,
            u'贷记卡账户数': data_list[4].content,
            u'首张贷记卡 发卡月份': data_list[5].content,
            u'准贷记卡账户数': data_list[6].content,
            u'首张准贷记卡发卡月份': data_list[7].content,
            u'本人声明数目': data_list[8].content,
            u'异议标注数目': data_list[9].content
        }


    def get_alive_debit_card_infor(self):
        """未销户贷记卡信息汇总"""
        start_index = self.get_index(u'未销户贷记卡信息汇总')
        if start_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1, number=8)
        return {
            u'发卡法人机构数': data_list[0].content,
            u'发卡机构数': data_list[1].content,
            u'账户数': data_list[2].content,
            u'授信总额': data_list[3].content,
            u'单家行最高授信额': data_list[4].content,
            u'单家行最低授信额': data_list[5].content,
            u'已用额度': data_list[6].content,
            u'最近6个月平均使用额度': data_list[7].content
        }
    def get_alive_loan_infor(self):
        """未结清贷款信息汇总"""
        start_index = self.get_index(u'未结清贷款信息汇总')
        if start_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1, number=6)
        return {
            u'贷款法人机构数': data_list[0].content,
            u'贷款机构数': data_list[1].content,
            u'笔数': data_list[2].content,
            u'合同总额': data_list[3].content,
            u'余额': data_list[4].content,
            u'最近6个月平均应还款': data_list[5].content,
        }

    def get_alive_semi_card_infor(self):
        """未销户准贷记卡信息汇总"""
        start_index = self.get_index(u'未销户准贷记卡信息汇总')
        if start_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1, number=8)
        return {
            u'发卡法人机构数': data_list[0].content,
            u'发卡机构数': data_list[1].content,
            u'账户数': data_list[2].content,
            u'授信总额': data_list[3].content,
            u'单家行最高授信额': data_list[4].content,
            u'单家行最低授信额': data_list[5].content,
            u'已用额度': data_list[6].content,
            u'最近6个月平均使用额度': data_list[7].content
        }

    def get_overdue_infor(self):
        """逾期（透支）信息汇总"""
        start_index = self.get_index(u'逾期（透支）信息汇总')
        if start_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1, number=12)
        return {
            u'贷款笔数': data_list[0].content,
            u'贷款逾期月份数': data_list[1].content,
            u'贷款单月最高逾期总额': data_list[2].content,
            u'贷款最长逾期月数': data_list[3].content,
            u'贷记卡账户数': data_list[4].content,
            u'贷记卡逾期月份数': data_list[5].content,
            u'贷记卡单月最高逾期总额': data_list[6].content,
            u'贷记卡最长逾期月数': data_list[7].content,
            u'准贷记卡账户数': data_list[8].content,
            u'准贷记卡透支月份数': data_list[9].content,
            u'准贷记卡单月最高透支余额': data_list[10].content,
            u'准贷记卡最长透支月份数': data_list[11].content
        }
    
    def get_query_summary_infor(self):
        """获得查询记录汇总"""
        start_index = self.get_index(u'查询记录汇总')
        if start_index == PDFParser.NO_INDEX:
            return None
        start_index = self.get_index(u'担保资格审查', start_index+1)
        start_index = self.get_index(u'审查', start_index+1)
        text_box_list = self.text_box_list[start_index+1:]
        data_list = PDFTools.filter_text_box_by_height(
            text_box_list, max_height=PDFParser.CONTENT_HEIGHT + 1,
            mini_height=PDFParser.CONTENT_HEIGHT - 1, number=8)
        return {
            u'贷款审批查询机构数': data_list[0].content,
            u'信用卡审批机构数': data_list[1].content,
            u'贷款审批数': data_list[2].content,
            u'信用卡审批查询数': data_list[3].content,
            u'本人查询数': data_list[4].content,
            u'贷后管理查询数': data_list[5].content,
            u'担保资格审查查询数': data_list[6].content,
            u'特约商户实名审查查询数': data_list[7].content
        }
    def get_loan(self):
        """获得贷款信息"""
        pass

    def get_debit_card(self):
        """获得贷记卡信息"""
        pass

    def get_semicard(self):
        """获得准贷记卡信息"""
        pass

    def get_personal_query(self):
        """获得个人查询信息"""
        start_index = self.get_index(u'本人查询记录明细')
        if start_index == PDFParser.NO_INDEX:
            return None
        end_index = self.get_index(u'报告说明')
        if end_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index + 1:end_index]
        data_list = PDFTools.filter_by_font(text_box_list,
                                            PDFParser.CONTENT_FONT)
        number = PDFTools.get_same_name_text_box(text_box_list, u'编号') [0]

        query_date = PDFTools.get_same_name_text_box(text_box_list,
                                                     u'查询日期') [0]
        query_oper = PDFTools.get_same_name_text_box(text_box_list,
                                                     u'查询操作员') [
            0]
        query_reason = PDFTools.get_same_name_text_box(text_box_list,
                                                       u'查询原因') [0]
        firsts_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number, None, None, query_date)
        merge_box = PDFTools.get_merge_text_box
        querys = list()
        for i in range(len(firsts_numbers)):
            if i == 0:
                up = number
            else:
                up = firsts_numbers [i - 1]
            if i == len(firsts_numbers) - 1:
                bottom = None
            else:
                bottom = firsts_numbers [i + 1]
            query = {
                u'编号': firsts_numbers [i].content,
                u'查询日期': merge_box(data_list, up, bottom, firsts_numbers [i],
                                   query_oper).content,
                u'查询操作员': merge_box(data_list, up, bottom, query_date,
                                    query_reason).content,
                u'查询原因': merge_box(data_list, up, bottom, query_oper,
                                   None).content,
            }
            querys.append(query)
        return querys


    def get_orgpro_query(self):
        """获得机构查询信息"""
        start_index = self.get_index(u'机构查询记录明细')
        if start_index == PDFParser.NO_INDEX:
            return None
        end_index = self.get_index(u'本人查询记录明细')
        if end_index == PDFParser.NO_INDEX:
            return None
        text_box_list = self.text_box_list[start_index + 1:end_index]
        data_list = PDFTools.filter_by_font(text_box_list,
                                            PDFParser.CONTENT_FONT)
        number = PDFTools.get_same_name_text_box(text_box_list, u'编号') [0]

        query_date = PDFTools.get_same_name_text_box(text_box_list,
                                                     u'查询日期')[0]
        query_oper = PDFTools.get_same_name_text_box(text_box_list,
                                                     u'查询操作员')[
            0]
        query_reason = PDFTools.get_same_name_text_box(text_box_list,
                                                     u'查询原因')[0]
        firsts_numbers = PDFTools.filter_text_box_by_other_text_box(
            data_list, number, None , None, query_date)
        merge_box = PDFTools.get_merge_text_box
        querys = list()
        for i in range(len(firsts_numbers)):
            if i == 0:
                up = number
            else:
                up = firsts_numbers[i-1]
            if i == len(firsts_numbers) - 1:
                bottom = None
            else:
                bottom = firsts_numbers[i+1]
            query = {
                u'编号': firsts_numbers[i].content,
                u'查询日期': merge_box(data_list, up, bottom, firsts_numbers[i],
                                   query_oper).content,
                u'查询操作员': merge_box(data_list, up, bottom, query_date,
                                   query_reason).content,
                u'查询原因': merge_box(data_list, up, bottom, query_oper,
                                 None).content,
            }
            querys.append(query)
        return querys


if __name__ == '__main__':
    parser = PDFParser('zqx.pdf')
    works = parser.get_works()
    livings = parser.get_living()
    report_infor = parser.get_report_infor()
    query_infor = parser.get_query_infor()
    person = parser.get_person()
    credit_tips = parser.get_credit_tips()
    couple = parser.get_couple()
    query_summary_infor = parser.get_query_summary_infor()
    personal_query = parser.get_personal_query()
    org_query = parser.get_orgpro_query()
    alive_debit_card_infor = parser.get_alive_debit_card_infor()
    alive_semi_infor = parser.get_alive_semi_card_infor()
    alice_loan_infor = parser.get_alive_loan_infor()
    pass


