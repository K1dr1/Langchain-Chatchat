from langchain.text_splitter import CharacterTextSplitter
import re
from typing import List


class ChineseTextSplitter(CharacterTextSplitter):
    def __init__(self, pdf: bool = False, sentence_size: int = 250, **kwargs):
        super().__init__(**kwargs)
        self.pdf = pdf
        self.sentence_size = sentence_size

    def split_text1(self, text: str) -> List[str]:
        if self.pdf:
            text = re.sub(r"\n{3,}", "\n", text)
            text = re.sub('\s', ' ', text)
            text = text.replace("\n\n", "")
        sent_sep_pattern = re.compile('([﹒﹔﹖﹗．。！？]["’”」』]{0,2}|(?=["‘“「『]{1,2}|$))')  # del ：；
        sent_list = []
        for ele in sent_sep_pattern.split(text):
            if sent_sep_pattern.match(ele) and sent_list:
                sent_list[-1] += ele
            elif ele:
                sent_list.append(ele)
        return sent_list

    def split_text(self, text: str) -> List[str]:
        if self.pdf:
            text = self._clean_pdf_text(text)

        text = self._apply_sentence_splitting_rules(text)
        return self._split_long_sentences(text)

    def _clean_pdf_text(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n", text)
        text = re.sub('\s', " ", text)
        return text.replace("\n\n", "")

    def _apply_sentence_splitting_rules(self, text: str) -> str:
        text = re.sub(r'([;；.!?。！？\?])([^”’])', r"\1\n\2", text)  # 单字符断句符
        text = re.sub(r'(\.{6})([^"’”」』])', r"\1\n\2", text)  # 英文省略号
        text = re.sub(r'(\…{2})([^"’”」』])', r"\1\n\2", text)  # 中文省略号
        text = re.sub(r'([;；!?。！？\?]["’”」』]{0,2})([^;；!?，。！？\?])', r'\1\n\2', text)
        return text

    def _split_long_sentences(self, text: str) -> List[str]:
        ls = [i for i in text.split("\n") if i]
        for ele in ls:
            if len(ele) > self.sentence_size:
                ele = self._split_if_long(ele)
        return ls

    def _split_if_long(self, text: str) -> str:
        ele1_ls = re.sub(r'([,，.]["’”」』]{0,2})([^,，.])', r'\1\n\2', text).split("\n")
        for ele_ele1 in ele1_ls:
            if len(ele_ele1) > self.sentence_size:
                ele_ele2 = re.sub(r'([\n]{1,}| {2,}["’”」』]{0,2})([^\s])', r'\1\n\2', ele_ele1)
                ele2_ls = ele_ele2.split("\n")
                for ele_ele2 in ele2_ls:
                    if len(ele_ele2) > self.sentence_size:
                        ele_ele3 = re.sub('( ["’”」』]{0,2})([^ ])', r'\1\n\2', ele_ele2)
                        ele2_id = ele2_ls.index(ele_ele2)
                        ele2_ls[ele2_id:ele2_id+1] = [i for i in ele_ele3.split("\n") if i]
                ele_id = ele1_ls.index(ele_ele1)
                ele1_ls[ele_id:ele_id+1] = [i for i in ele2_ls if i]
        return "\n".join(ele1_ls)

# 测试代码
if __name__ == "__main__":
    text_splitter = ChineseTextSplitter(
        pdf=False,
        sentence_size=250
    )
    text = "文本内容"
    chunks = text_splitter.split_text(text)
    for chunk in chunks:
        print(chunk)


