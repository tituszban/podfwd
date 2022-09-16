from ssml import tags, RawText


def test_replace():
    speech = tags.Speak([
        tags.P(
            tags.S(
                RawText("Hello world!")
            )
        ),
        RawText("Hello? World?worldworld")
    ])

    assert speech.to_string() == '<speak><p><s>Hello world!</s></p>Hello? World?worldworld</speak>'

    replaced = speech.replace_text("world", lambda t: tags.Emphasis(RawText(t), level="strong"))

    assert replaced is not None
    assert replaced.to_string() == '<speak><p><s>Hello <emphasis level="strong">world</emphasis>!</s></p>Hello? World?<emphasis level="strong">world</emphasis><emphasis level="strong">world</emphasis></speak>'

def test_replace_ignore_case():
    speech = tags.Speak([
        tags.P(
            tags.S(
                RawText("Hello world!")
            )
        ),
        RawText("Hello? World?worldworld")
    ])

    assert speech.to_string() == '<speak><p><s>Hello world!</s></p>Hello? World?worldworld</speak>'

    replaced = speech.replace_text("world", lambda t: tags.Emphasis(RawText(t), level="strong"), ignore_case=True)

    assert replaced is not None
    assert replaced.to_string() == '<speak><p><s>Hello <emphasis level="strong">world</emphasis>!</s></p>Hello? <emphasis level="strong">World</emphasis>?<emphasis level="strong">world</emphasis><emphasis level="strong">world</emphasis></speak>'
