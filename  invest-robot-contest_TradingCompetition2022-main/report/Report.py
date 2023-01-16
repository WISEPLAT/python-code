from fpdf import FPDF
from abc import ABC, abstractmethod
from account.Account import Account


class ReportBuilder:

    @classmethod
    def buildSessionResultReport(cls, report_name, report_source):
        return SessionResultReport(report_name=report_name, report_source=report_source)


class Report(ABC):
    def __init__(self, report_name, report_source):
        self._report_source = report_source
        self._report_name = report_name
        pass

    @abstractmethod
    def pdf_generator(self):
        pass

    def save_to_pdf(self, file_name) -> object:
        """
        Save pdf
        :param file_name:
        :return:
        """
        pdf = self.pdf_generator()
        # save the pdf with name .pdf
        out_file = "report/result/" + file_name + ".pdf"
        pdf.output(out_file)
        return out_file


class SessionResultReport(Report):

    def pdf_generator(self) -> object:
        """
        Generate pdf
        :return:
        """
        pdf = FPDF()
        pdf.add_page()
        family = "Sans"
        family_name = "report/Open_Sans/static/OpenSans/OpenSans-Regular.ttf"
        pdf.add_font(family, style="", fname=family_name, uni=True)
        pdf.set_font(family, size=15)
        w, h = 200, 10
        pdf.cell(w, h, txt="RESULT OF TRADING SESSION", ln=1, align='C')
        pdf.cell(w, h, txt="SESSION ID" + self._report_name, ln=1, align='C')
        pdf.cell(200, 10, txt="", ln=2, align='L')

        pdf.set_font(family, size=9)

        pdf.cell(w, h,
                 txt="Всего выполнено ордеров алгоритмом: " + str(self._report_source['count_orders']),
                 ln=1, align='L')
        pdf.cell(w, h,
                 txt="Всего выполнено ордеров на открытие лонг позиций: " +
                     str(self._report_source['count_long_opened']),
                 ln=1, align='L')
        pdf.cell(w, h,
                 txt="Всего выполнено ордеров на закрытие лонг позиций: " +
                     str(self._report_source['count_long_closed']),
                 ln=1, align='L')
        pdf.cell(200, 10, txt="", ln=2, align='L')

        def __write_operation(operation_type, pdf_link, source):
            idx = 0
            for i in source[operation_type]:
                idx += 1
                payment = "(Сумма = " + str(Account.convert_out(i['payment']))
                quantity = " количество = " + str(i['quantity'])
                txt = str(idx) + ") " + str(i['name']) + payment + " " + i['currency'] + quantity + " )"
                pdf_link.cell(w, h, txt, ln=1, align='L')
            return pdf_link

        pdf.cell(w, h, txt="Операции, зафиксированные брокером", ln=1, align='C')

        pdf.cell(w, h, txt="Покупка", ln=1, align='C')
        pdf = __write_operation(operation_type='buy', pdf_link=pdf, source=self._report_source)
        pdf.cell(200, 10, txt="", ln=2, align='L')

        pdf.cell(w, h, txt="Продажа", ln=1, align='C')
        pdf = __write_operation(operation_type='sell', pdf_link=pdf, source=self._report_source)
        pdf.cell(200, 10, txt="", ln=2, align='L')

        pdf.cell(200, 10, txt="Комиссия брокера " + str(Account.convert_out(self._report_source['sum_fee'])),
                 ln=2, align='L')

        return pdf
