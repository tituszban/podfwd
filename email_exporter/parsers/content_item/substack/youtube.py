from ..content_item_abc import ContentItemABC
import re

"""
<a class="m_2243634152544061959youtube-wrap" href="https://email.mg2.substack.com/c/eJwlkMtqhTAQhp_GLMXcjC6yKJRTuuwTSC5zPKGaiE6O2KdvVJgLM8Pw83_OIIxpPfSSNiRnGfBYQEfYtwkQYSV5g3UIXnPRs7Zpe-K18LSTHQnb8FwBZhMmjWsGsmQ7BWcwpHh9SC4keWlrpO-tYY1Ugj6lkL1RXlHpveUWpL11TfYBogMNb1iPFIFM-oW4bBX_qNijxL7v9ZEyZgu1S_O5MeheFX-8K_5pl6-Aj-8_M_-QoFnDaNNdKRtW0xoU5QwE5c60pleeQ9d09Nn2TvROKVWJZh5ZvWW7oXG_pwBZNQbM2581sZzH0-i1Lz6H0uccAx4DRGMn8DcCvEleUIYRIqyFsB8MatqyvgDhVLKO35YLI9GwMgtFirBP5SvqmMxrCbFA_Ae2AopV" style="display:block;margin:1.6em 0" target="_blank">
 <img src="https://cdn.substack.com/image/youtube/w_550,c_limit/l_youtube_play_qyqt8q,w_120/bpGitFIzamQ" style="border:none!important;display:block;height:auto;margin:0 auto;max-width:550px;vertical-align:middle;width:100%"/>
</a>
"""


class Youtube(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        if component.name == "a" and "class" in component.attrs and any(class_.endswith("youtube-wrap") for class_ in component["class"]):
            return True

        return False
