from ..content_item_abc import ContentItemABC
from ... import speech_item

"""
<table align="center" border="0" cellpadding="0" cellspacing="0" style="max-width:600px;" width="100%">
 <!-- Logo -->
 <tr>
  <td align="center" style="padding: 40px 0 0 0;" valign="top">
   <a href="https://link.techcrunch.com/click/25016890.55889/aHR0cHM6Ly90ZWNoY3J1bmNoLmNvbT91dG1fbWVkaXVtPVRDbmV3c2xldHRlciZ0cGNjPVRDc3RhcnR1cHNuZXdzbGV0dGVyJnV0bV9jYW1wYWlnbj1UQ3N0YXJ0dXBzd2Vla2x5/5efa60b389f523479b4459bbB0458d154" style="text-decoration: none" target="_blank">
    <img alt="TechCrunch logo" border="0" src="https://sailthru-media.s3.amazonaws.com/composer/images/sailthru-prod-134/Logos/tc-mark-2017.png" style="margin:0; padding:0; max-width: 100px; border: none; display: block;"/>
   </a>
  </td>
 </tr>
 <tr>
  <td align="center" style="padding: 30px 0 15px 0;" valign="top">
   <a href="https://link.techcrunch.com/click/25016890.55889/aHR0cHM6Ly90ZWNoY3J1bmNoLmNvbT91dG1fbWVkaXVtPVRDbmV3c2xldHRlciZ0cGNjPVRDc3RhcnR1cHNuZXdzbGV0dGVyJnV0bV9jYW1wYWlnbj1UQ3N0YXJ0dXBzd2Vla2x5/5efa60b389f523479b4459bbC0458d154" style="text-decoration: none" target="_blank">
    <img alt="Startups Weekly logo" border="0" src="https://sailthru-media.s3.amazonaws.com/composer/images/sailthru-prod-134/Logos/startups-weekly-logo-gradient.png" style="margin:0; padding:0; max-width: 280px; border:none; display:block;"/>
   </a>
  </td>
 </tr>
 <!-- ./Logo -->
 <!-- Author -->
 <tr>
  <td align="center" style="padding: 0 0 30px 0; font-family: Helvetica, Arial, sans-serif;" valign="top">
   <p style="color: #5a5a5a; font-size: 18px; font-weight: bold; line-height: 28px; margin: 0;">
    Saturday, September 11, 2021
    <span style="color: #d8d8d8; margin-left: 3px; margin-right: 3px;">
     •
    </span>
    By
    <span style="color: #14c435">
     <a href="https://link.techcrunch.com/click/25016890.55889/aHR0cHM6Ly90ZWNoY3J1bmNoLmNvbS9hdXRob3IvbmF0YXNoYS1tYXNjYXJlbmhhcz91dG1fbWVkaXVtPVRDbmV3c2xldHRlciZ0cGNjPVRDc3RhcnR1cHNuZXdzbGV0dGVyJnV0bV9jYW1wYWlnbj1UQ3N0YXJ0dXBzd2Vla2x5/5efa60b389f523479b4459bbBb5763eb5" style="font-family: Helvetica, Arial; color: #14c435; text-decoration: none;" target="_blank">
      Natasha Mascarenhas
     </a>
    </span>
   </p>
  </td>
 </tr>
 <!-- ./Author -->
</table>
"""

class Header(ContentItemABC):
    def __init__(self, component, to_item, inbox_item=None):
        super().__init__(component, to_item)
        assert inbox_item, "Header requires inbox_item parameter"
        self._inbox_item = inbox_item

    def get_ssml(self):
        title = self._inbox_item.title.replace("\r\n", "")
        author = self._get_text_content().replace("•", ";")
        return [
            speech_item.Paragraph(title),
            speech_item.Paragraph(author),
            speech_item.Pause("750ms")
        ]

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        return False
