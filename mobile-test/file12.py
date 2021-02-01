from kivy.lang import Builder

from kivymd.app import MDApp

from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.tab import MDTabsBase

KV = '''
#https://stackoverflow.com/questions/65698145/kivymd-tab-name-containing-icons-and-text
# this import will prevent disappear tabs through some clicks on them)))
#:import md_icons kivymd.icon_definitions.md_icons
#:import fonts kivymd.font_definitions.fonts

Screen:

    MDNavigationLayout:

        ScreenManager:

            Screen:

                BoxLayout:
                    orientation: 'vertical'

                    MDTabs:
                        id: tabs                     
                        height: "48dp"
                        tab_indicator_anim: False

                        Tab:
                            id: tab1
                            name: 'tab1'
                            text: f"[size=20][font={fonts[-1]['fn_regular']}]{md_icons['star']}[/size][/font] Star"

                            BoxLayout:
                                orientation: 'vertical'
                                padding: "10dp"   

                                BoxLayout:
                                    orientation: 'horizontal'                               

                                    MDIconButton:
                                        icon: "calendar"

                                    MDTextField:
                                        id: start_date
                                        hint_text: "Date"
                                        text: "Why this text grey? I want blue text here!!! (with no Focus)"                                      
                                        text_hint_color:[0,0,1,1]                                     

                                BoxLayout:
                                    orientation: 'horizontal'                         

                                    MDIconButton:
                                        icon: "cash"

                                    MDTextField:
                                        id: test
                                        hint_text: "test"
                                        text: "Why this text grey? I want blue text here!!!"
                                        text_hint_color:[0,0,1,1]
                        Tab:
                            id: tab2
                            name: 'tab2'
                            text: f"[size=20][font={fonts[-1]['fn_regular']}]{md_icons['star']}[/size][/font] Star 2"

                            BoxLayout:
                                orientation: 'vertical'
                                padding: "10dp"   

                                BoxLayout:
                                    orientation: 'horizontal'                               

                                    MDIconButton:
                                        icon: "calendar"

                                    MDTextField:
                                        id: start_date2
                                        hint_text: "Date"                                      

                                BoxLayout:
                                    orientation: 'horizontal'                         

                                    MDIconButton:
                                        icon: "cash"

                                    MDTextField:
                                        id: test2
                                        hint_text: "test2"

                        Tab:
                            id: tab3
                            name: 'tab3'
                            text: f"[size=20][font={fonts[-1]['fn_regular']}]{md_icons['star']}[/size][/font] Star3"

                            BoxLayout:
                                orientation: 'vertical'
                                padding: "10dp"   

                                BoxLayout:
                                    orientation: 'horizontal'                               

                                    MDIconButton:
                                        icon: "calendar"

                                    MDTextField:
                                        id: start_date3
                                        hint_text: "Date"                                      

                                BoxLayout:
                                    orientation: 'horizontal'                         

                                    MDIconButton:
                                        icon: "cash"

                                    MDTextField:
                                        id: test3
                                        hint_text: "test3"



'''


class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class TestApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)

    def build(self):
        self.theme_cls.theme_style = "Light"  # "Dark"  # "Light"
        # return Builder.load_string(KV)
        return self.screen

    def on_start(self):
        pass

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        pass


TestApp().run()
