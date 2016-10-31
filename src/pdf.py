# coding:utf-8
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import *
from pdfminer.converter import PDFPageAggregator
import random

""" PDF对象内容"""


class TextBOX(object):
    """ 文本框"""
    def __init__(self, content, start_x, start_y, end_x, end_y, font_dict):
        """文本框中包含文本[内容,宽度,高度,start_x,start_y,end_x,end_y,page_no]"""
        self.content = content
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.font_dict = font_dict
        self.width = self.end_x - self.start_y
        self.height = self.end_y - self.start_y

    def reset_text_box(self, start_x=None, start_y=None, end_x=None, 
                       end_y=None, content=None, font_dict=None):
        """
        重置页面框的起始终止xy值,page_no
        :param start_x:
        :param start_y:
        :param end_x:
        :param end_y:
        :param content:
        :param font_dict:
        :return:
        """
        if start_x is not None:
            self.start_x = start_x
        if start_y is not None:
            self.start_y = start_y
        if end_x is not None:
            self.end_x = end_x
        if end_y is not None:
            self.end_y = end_y
        if content is not None:
            self.content = content
        if font_dict is not None:
            self.font_dict = font_dict
        self.width = self.end_x - self.start_x
        self.height = self.end_y - self.start_y

class PageBOX(object):
    """页面框"""
    def __init__(self, start_x, start_y, end_x, end_y,
                 page_no=None):

        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.width = self.end_x - self.start_y
        self.height = self.end_y - self.start_y
        self.page_no = page_no
        self.text_box_list = list()

    def add_text_box(self, text_box=None):
        """
        添加一个text_box
        :param text_box:
        :return:
        """
        if text_box is None:
            return None
        self.text_box_list.append(text_box)

    def reset_page_box(self, start_x=None, start_y=None, end_x=None, 
                       end_y=None, page_no=None):
        """
        重置页面框的起始终止xy值,page_no
        :param start_x:
        :param start_y:
        :param end_x:
        :param end_y:
        :param page_no:
        :return:
        """
        if start_x is not None:
            self.start_x = start_x
        if start_y is not None:
            self.start_y = start_y
        if end_x is not None:
            self.end_x = end_x
        if end_y is not None:
            self.end_y = end_y
        self.page_no = page_no
        self.width = self.end_x - self.start_x
        self.height = self.end_y - self.start_y

    def reset_text_box_list(self, offset_x=None, offset_y=None):
        """
        给page 中的text_box 添加位置偏移量
        :param offset_x:
        :param offset_y:
        :return:
        """
        if offset_y is None:
            offset_y = 0
        if offset_x is None:
            offset_x = 0
        for text_box in self.text_box_list:
            text_box.start_x += offset_x
            text_box.end_x += offset_x
            text_box.start_y += offset_y
            text_box.end_y += offset_y

    def filter_text_box(self, start_x=None, start_y=None, end_x=None,
                        end_y=None):
        """
        根据设定的坐标区域过滤掉不在内的text_box
        :param start_x:
        :param start_y:
        :param end_x:
        :param end_y:
        :return:
        """
        if start_x is None:
            start_x = 0
        if start_y is None:
            start_y = 0
        if end_x is None:
            end_x = PDFTools.MAX_NUM
        if end_y is None:
            end_y = PDFTools.MAX_NUM
        new_text_box_list = list()
        for text_box in self.text_box_list:
            if text_box.start_x < start_x:
                continue
            if text_box.start_y < start_y:
                continue
            if text_box.end_x > end_x:
                continue
            if text_box.end_y > end_y:
                continue
            new_text_box_list.append(text_box)
        self.text_box_list = new_text_box_list
        return self.text_box_list


class PDFTools(object):
    """PDF 内容处理工具方法"""
    # 最大长度或宽度
    MAX_NUM = 1000000
    PDF_X = 'x'
    PDF_Y = 'y'
    PDF_CONTENT_START_X = 60
    PDF_CONTENT_START_Y = 60
    PDF_CONTENT_END_X = 530
    PDF_CONTENT_END_Y = 785

    def __init__(self):
        pass

    @staticmethod
    def create_page_box():
        """创建一个页面框,默认所有字段为0"""
        return PageBOX(start_x=0, start_y=0,
                       end_x=0, end_y=0)

    @staticmethod
    def create_text_box():
        """创建一个文本框,默认所有字段为0"""
        return TextBOX(content=u'', start_x=0, start_y=0,
                       end_x=0, end_y=0, font_dict=dict())

    @staticmethod
    def merge_page_box(page_box_list=None):
        """
        合并页面框
        :param page_box_list:
        :return:
        """
        if page_box_list is None:
            return None
        for page_box in page_box_list:
            page_box.filter_text_box(start_x=PDFTools.PDF_CONTENT_START_X,
                                     end_x=PDFTools.PDF_CONTENT_END_X,
                                     start_y=PDFTools.PDF_CONTENT_START_Y,
                                     end_y=PDFTools.PDF_CONTENT_END_Y)
        sorted_list = PDFTools.sort_page_box(page_box_list)
        merge_box = PDFTools.create_page_box()
        for i in range(len(sorted_list)):
            page_box = sorted_list[i]
            page_box.reset_page_box(end_x=PDFTools.PDF_CONTENT_END_X,
                                    end_y=PDFTools.PDF_CONTENT_END_Y)
            page_box.reset_text_box_list(
                offset_x=-PDFTools.PDF_CONTENT_START_X,
                offset_y=-PDFTools.PDF_CONTENT_START_Y)
            page_box.reset_text_box_list(offset_y=merge_box.height)
            merge_box.reset_page_box(
                end_y=merge_box.height+page_box.height,
                end_x=PDFTools.PDF_CONTENT_END_X)
            merge_box.text_box_list += page_box.text_box_list

        return merge_box

    @staticmethod
    def sort_page_box(page_box_list=None):
        """
        对列表中page_box排序
        :param page_box_list:
        :return:
        """
        if len(page_box_list) < 2:
            return page_box_list
        pivot_page_box = random.choice(page_box_list)
        small = list()
        medium = list()
        large = list()
        for page_box in page_box_list:
            if page_box.page_no > pivot_page_box.page_no:
                small.append(page_box)
            elif page_box.page_no == pivot_page_box.page_no:
                medium.append(page_box)
            else:
                large.append(page_box)
        return PDFTools.sort_page_box(small) + medium + \
            PDFTools.sort_page_box(large)

    @staticmethod
    def merge_text_box(text_box_list=None):
        """
        :param text_box_list:
        :return:
        """
        if text_box_list is None:
            return None
        if len(text_box_list) == 1:
            return text_box_list[0]
        sorted_list = PDFTools.quick_sort_text_box(text_box_list)
        merge_box = sorted_list.pop(0)
        for i in range(len(sorted_list)):
            content = merge_box.content + sorted_list[i].content
            if merge_box.start_x > sorted_list[i].start_x:
                start_x = sorted_list[i].start_x
            else:
                start_x = merge_box.start_x
            if merge_box.start_y > sorted_list[i].start_y:
                start_y = sorted_list[i].start_y
            else:
                start_y = merge_box.start_y
            if merge_box.end_x < sorted_list[i].end_x:
                end_x = sorted_list[i].end_x
            else:
                end_x = merge_box.end_x
            if merge_box.end_y < sorted_list[i].end_y:
                end_y = sorted_list[i].end_y
            else:
                end_y = merge_box.end_y
            merge_box.reset_text_box(start_x=start_x, start_y=start_y,
                                     end_x=end_x, end_y=end_y, content=content)
        return merge_box

    @staticmethod
    def merge_box_base_x(text_box_list):
        new_text_box = text_box_list.pop(0)
        new_text_box_list = list()
        for text_box in text_box_list:
            if new_text_box.start_x <= text_box.start_x and \
                new_text_box.end_x >= text_box.end_x:
                new_text_box = PDFTools.merge_text_box(
                    [new_text_box, text_box])
            else:
                new_text_box_list.append(new_text_box)
                new_text_box = text_box
        new_text_box_list.append(new_text_box)
        return new_text_box_list


    @staticmethod
    def quick_sort_text_box_base_x(text_box_list):
        """

        :param text_box_list:
        :return:
        """
        if len(text_box_list) < 2:
            return text_box_list
        pivot_text_box = random.choice(text_box_list)
        small = list()
        medium = list()
        large = list()
        for text_box in text_box_list:
            if text_box.start_x < pivot_text_box.start_x:
                small.append(text_box)
            elif text_box.start_x == pivot_text_box.start_x:
                medium.append(text_box)
            else:
                large.append(text_box)
        return PDFTools.quick_sort_text_box_base_x(small) + medium \
            + PDFTools.quick_sort_text_box_base_x(large)

    @staticmethod
    def quick_sort_text_box(text_box_list):
        """
        对text box 根据排序对着进行排序
        :param text_box_list:
        :return:
        """
        if len(text_box_list) < 2:
            return text_box_list
        pivot_text_box = random.choice(text_box_list)
        small = list()
        medium = list()
        large = list()
        for text_box in text_box_list:
            if text_box.start_y > pivot_text_box.start_y:
                small.append(text_box)
            elif text_box.start_y < pivot_text_box.start_y:
                large.append(text_box)
            elif text_box.start_x < pivot_text_box.start_x:
                small.append(text_box)
            elif text_box.start_x == pivot_text_box.start_x:
                medium.append(text_box)
            else:
                large.append(text_box)
        return PDFTools.quick_sort_text_box(small) + medium \
            + PDFTools.quick_sort_text_box(large)

    @staticmethod
    def get_font_dict(box):
        objs = box._objs
        if objs is None or len(objs)==0:
            return dict()
        lt_chars = objs[0]._objs
        if lt_chars is None or len(lt_chars)==0:
            return dict()
        font_dict = dict()
        for lt_char in lt_chars:
            if not isinstance(lt_char, LTChar):
                continue
            if lt_char.fontname in font_dict.keys():
                font_dict[lt_char.fontname] += 1
            else:
                font_dict[lt_char.fontname] = 1
        return font_dict

    @staticmethod
    def parse_page_box(pdf_file_path, line_overlap=0.2, char_margin=0.1,
                       line_margin=0.2, word_margin=0.1, boxes_flow=0.5,
                       detect_vertical=False, all_texts=False):
        """
        创建一个PDF文档分析器
        创建一个PDF文档对象存储文档结构
        检查文件是否允许文本提取
        创建一个PDF资源管理器对象来存储共赏资源
        设定参数进行分析
        创建一个PDF设备对象
        创建一个PDF解释器对象
        处理每一页
        :param pdf_file_path:
        :param line_overlap:
        :param word_margin:
        :param line_margin:
        :param char_margin:
        :param boxes_flow:
        :param detect_vertical:
        :param all_texts:
        :return:
        """
        fp = open(pdf_file_path, 'rb')
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            resources_manger = PDFResourceManager()
            la_params = LAParams(line_overlap=line_overlap,
                                 detect_vertical=detect_vertical,
                                 all_texts=all_texts,
                                 word_margin=word_margin,
                                 line_margin=line_margin,
                                 char_margin=char_margin,
                                 boxes_flow=boxes_flow)
            device = PDFPageAggregator(resources_manger, laparams=la_params)
            interpreter = PDFPageInterpreter(resources_manger, device)
            page_no = 0
            page_box_list = list()
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
                layout = device.get_result()
                page_box = PDFTools.create_page_box()
                page_box.reset_page_box(start_x=layout.x0, start_y=layout.y0,
                                        end_x=layout.x1, end_y=layout.y1,
                                        page_no=page_no)
                for box in layout:
                    if isinstance(box, LTTextBoxHorizontal):
                        content = box.get_text().strip(u'\n ')
                        if content == u'':
                            continue
                        text_box = PDFTools.create_text_box()
                        font_dict = PDFTools.get_font_dict(box=box)
                        text_box.reset_text_box(start_x=box.x0, start_y=box.y0,
                                                end_x=box.x1, end_y=box.y1,
                                                content=content,
                                                font_dict=font_dict)
                        page_box.add_text_box(text_box=text_box)
                page_box_list.append(page_box)
                page_no += 1
            return page_box_list

    @staticmethod
    def get_page_box(file_path):
        page_box_list = PDFTools.parse_page_box(file_path)
        merge_page_box = PDFTools.merge_page_box(page_box_list)
        return merge_page_box

    @staticmethod
    def filter_text_box_by_height(text_box_list=None, max_height=None,
                                  mini_height=None, number=None):
        """根据高度来选择字段,并限制数目"""
        if text_box_list is None:
            return None
        if max_height is None:
            max_height = mini_height
        if mini_height is None:
            mini_height = max_height
        if max_height is None:
            return None
        filter_text_box = list()
        if number is None:
            number = len(text_box_list)
        for text_box in text_box_list:
            if text_box.height >= mini_height and text_box.height <= max_height:
                filter_text_box.append(text_box)
            if len(filter_text_box) == number:
                break
        return filter_text_box

    @staticmethod
    def get_same_name_text_box(text_box_list,name=None):
        if name is None:
            return text_box_list
        return [text_box for text_box in text_box_list if
                name in text_box.content]

    @staticmethod
    def get_text_box(self, text_box_list=None, special_text=None):
        """根据特征值获得相应的文本"""
        if text_box_list is None:
            return None
        if special_text is None:
            return None
        for text_box in text_box_list:
            if special_text in text_box.content:
                return text_box
        return None

    @staticmethod
    def filter_text_box_by_other_text_box(text_box_list=None, up=None,
                                          bottom=None, left=None, right=None):
        if text_box_list is None:
            return None
        if up is None:
            bottoms = text_box_list
        else:
            bottoms = [text_box for text_box in text_box_list if
                       text_box.end_y <= up.start_y]
        if bottom is None:
            ups = bottoms
        else:
            ups = [text_box for text_box in bottoms if
                   text_box.start_y >= bottom.end_y]
        if left is None:
            lefts = ups
        else:
            lefts = [text_box for text_box in ups if
                        text_box.start_x >= left.end_x]
        if right is None:
            rights = lefts
        else:
            rights = [text_box for text_box in lefts if
                        text_box.end_x <= right.start_x]
        return rights

    @staticmethod
    def get_merge_text_box(text_box_list=None, up=None,
                                          bottom=None, left=None, right=None):
        """获得指定范围的全部内容text_box"""
        data = PDFTools.filter_text_box_by_other_text_box(
            text_box_list, up, bottom, left, right)
        return PDFTools.merge_text_box(
            PDFTools.filter_text_box_by_other_text_box(text_box_list, up,
                                                       bottom, left, right))

    @staticmethod
    def filter_by_font(text_box_list, font):
        if text_box_list is None:
            return  text_box_list
        if font is None:
            return text_box_list
        filter_list = list()
        for text_box in text_box_list:
            if font in text_box.font_dict.keys():
                filter_list.append(text_box)
        return filter_list

if __name__ == '__main__':
    page_box_list = PDFTools.parse_page_box('zqx.pdf')
    merge_page_box = PDFTools.merge_page_box(page_box_list=page_box_list)
    text_box_list = PDFTools.quick_sort_text_box(merge_page_box.text_box_list)
    for box in text_box_list:
        print box.content


