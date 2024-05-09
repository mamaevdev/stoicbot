import json
import unittest
from parser import RESULT_FILE_PATH, END_QUOTE_SYMBOL, START_SOURCE_SYMBOL, Parser


# Test resulted JSON file
class TestJsonResult(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    @classmethod
    def setUpClass(cls):
        with open(RESULT_FILE_PATH) as file:
            cls.data = json.load(file)

    # Tests for Parser.__is_end_of_quote
    def test__is_end_of_quote(self):
        # Test case: line ends with END_QUOTE_SYMBOL
        self.assertTrue(
            self.parser._Parser__is_end_of_quote(
                f"This is a quote: {END_QUOTE_SYMBOL}", "Next line"
            )
        )

        # Test case: next line starts with START_SOURCE_SYMBOL and next five characters are uppercase
        self.assertTrue(
            self.parser._Parser__is_end_of_quote(
                "There is no end quote symbol", f"{START_SOURCE_SYMBOL}SOURCE EXAMPLE"
            )
        )

        # Test case: next line starts with five uppercase characters
        self.assertTrue(
            self.parser._Parser__is_end_of_quote(
                "There is no end quote symbol",
                "SOURCE EXAMPLE without start source symbol",
            )
        )

        # Test case: none of the conditions are met
        self.assertFalse(
            self.parser._Parser__is_end_of_quote(
                "There is no end quote symbol", "Next line"
            )
        )

    # Tests for Parser.__parse_letter_date_title
    def test__parse_letter_date_title(self):
        # Test case: first letter is not empty
        lines = [
            "E",
            "January 1st",
            "EXPECTED TITLE",
            "“Expected quote",
            "expected quote”",
            "—EXPECTED SOURCE",
            "xpected explanation",
            "expected explanation",
            "expected explanation.",
        ]
        expected_result = (
            "E",
            "January 1st",
            "EXPECTED TITLE",
            [
                "“Expected quote",
                "expected quote”",
                "—EXPECTED SOURCE",
                "xpected explanation",
                "expected explanation",
                "expected explanation.",
            ],
        )
        self.assertEqual(
            self.parser._Parser__parse_letter_date_title(lines), expected_result
        )

        # Test case: first letter is prefixed anf title is multiline
        lines = [
            "#E",
            "January 1st",
            "EXP",
            "ECT",
            "ED TI",
            "TLE",
            "“Expected quote",
            "expected quote”",
            "—EXPECTED SOURCE",
            "xpected explanation",
            "expected explanation",
            "expected explanation.",
        ]
        expected_result = (
            "#E",
            "January 1st",
            "EXPECTED TITLE",
            [
                "“Expected quote",
                "expected quote”",
                "—EXPECTED SOURCE",
                "xpected explanation",
                "expected explanation",
                "expected explanation.",
            ],
        )
        self.assertEqual(
            self.parser._Parser__parse_letter_date_title(lines), expected_result
        )

    # Tests for Parser.__parse_page_text
    def test__parse_page_text(self):
        # Test case: first letter is not empty and correct quote format
        text = """E
          January 1st
          EXPECTED TITLE
          “Expected quote
          expected quote”
          —EXPECTED SOURCE
          xpected explanation
          expected explanation
          expected explanation.
        """
        expected_result = (
            "January 1",
            "EXPECTED TITLE",
            "“Expected quote expected quote”",
            "—EXPECTED SOURCE",
            "Expected explanation expected explanation expected explanation.",
        )
        self.assertEqual(self.parser._Parser__parse_page_text(text), expected_result)

        # Test case: first letter is empty and quote is missing END_QUOTE_SYMBOL and START_SOURCE_SYMBOL
        text = """January 1st
          EXPECTED TITLE
          “Expected quote
          expected quote
          EXPECTED SOURCE
          Expected explanation
          expected explanation
          expected explanation.
        """
        expected_result = (
            "January 1",
            "EXPECTED TITLE",
            "“Expected quote expected quote”",
            "—EXPECTED SOURCE",
            "Expected explanation expected explanation expected explanation.",
        )
        self.assertEqual(self.parser._Parser__parse_page_text(text), expected_result)

    # Check if result JSON file has 366 entries
    def test_total_entries(self):
        self.assertEqual(len(self.data), 366)

    # Check if some dates are correct
    def test_dates(self):
        dates = list(self.data.keys())
        self.assertEqual(dates[0], "January 1")
        self.assertEqual(dates[7], "January 8")  # Missing closing quote symbol
        self.assertEqual(dates[20], "January 21")  # Complex stoic structure
        self.assertEqual(dates[30], "January 31")
        self.assertEqual(dates[31], "February 1")
        self.assertEqual(dates[37], "February 7")  # First letter is prefixed with quote
        self.assertEqual(dates[39], "February 9")  # Multiline title
        self.assertEqual(dates[59], "February 29")
        self.assertEqual(dates[60], "March 1")
        self.assertEqual(dates[90], "March 31")
        self.assertEqual(dates[91], "April 1")
        self.assertEqual(dates[120], "April 30")
        self.assertEqual(dates[121], "May 1")
        self.assertEqual(dates[151], "May 31")
        self.assertEqual(dates[152], "June 1")
        self.assertEqual(dates[181], "June 30")
        self.assertEqual(dates[182], "July 1")
        self.assertEqual(dates[210], "July 29")  # Missing start source symbol
        self.assertEqual(dates[212], "July 31")
        self.assertEqual(dates[213], "August 1")
        self.assertEqual(dates[243], "August 31")
        self.assertEqual(dates[244], "September 1")
        self.assertEqual(dates[273], "September 30")
        self.assertEqual(dates[274], "October 1")
        self.assertEqual(dates[304], "October 31")
        self.assertEqual(dates[305], "November 1")
        self.assertEqual(dates[334], "November 30")
        self.assertEqual(dates[335], "December 1")
        self.assertEqual(dates[365], "December 31")

    # Check if some titles are correct
    def test_titles(self):
        self.assertEqual(self.data["January 1"]["title"], "CONTROL AND CHOICE")
        self.assertEqual(self.data["January 8"]["title"], "SEEING OUR ADDICTIONS")
        self.assertEqual(self.data["January 21"]["title"], "A MORNING RITUAL")
        self.assertEqual(
            self.data["February 7"]["title"], "FEAR IS A SELF-FULFILLING PROPHECY"
        )
        self.assertEqual(
            self.data["February 9"]["title"], "YOU DON\u2019T HAVE TO HAVE AN OPINION"
        )
        self.assertEqual(self.data["July 29"]["title"], "A CURE FOR THE SELF")
        self.assertEqual(
            self.data["December 31"]["title"], "GET ACTIVE IN YOUR OWN RESCUE"
        )

    # Check if some quotes are correct
    def test_quotes(self):
        self.assertEqual(
            self.data["January 1"]["quote"],
            "\u201cThe chief task in life is simply this: to identify and separate matters so that I can say clearly to myself which are externals not under my control, and which have to do with the choices I actually control. Where then do I look for good and evil? Not to uncontrollable externals, but within myself to the choices that are my own . . .\u201d",
        )
        self.assertEqual(
            self.data["January 8"]["quote"],
            "\u201cWe must give up many things to which we are addicted, considering them to be good. Otherwise, courage will vanish, which should continually test itself. Greatness of soul will be lost, which can\u2019t stand out unless it disdains as petty what the mob regards as most desirable.\u201d",
        )
        self.assertEqual(
            self.data["January 21"]["quote"],
            "\u201cAsk yourself the following first thing in the morning: What am I lacking in attaining freedom from passion? What for tranquility? What am I? A mere body, estate-holder, or reputation? None of these things. What, then? A rational being. What then is demanded of me? Meditate on your actions. How did I steer away from serenity? What did I do that was unfriendly, unsocial, or uncaring? What did I fail to do in all these things?\u201d",
        )
        self.assertEqual(
            self.data["February 7"]["quote"],
            "\u201cMany are harmed by fear itself, and many may have come to their fate while dreading fate.\u201d",
        )
        self.assertEqual(
            self.data["February 9"]["quote"],
            "\u201cWe have the power to hold no opinion about a thing and to not let it upset our state of mind\u2014for things have no natural power to shape our judgments.\u201d",
        )
        self.assertEqual(
            self.data["July 29"]["quote"],
            "\u201cThe person who has practiced philosophy as a cure for the self becomes great of soul, filled with confidence, invincible\u2014and greater as you draw near.\u201d",
        )
        self.assertEqual(
            self.data["December 31"]["quote"],
            "\u201cStop wandering about! You aren\u2019t likely to read your own notebooks, or ancient histories, or the anthologies you\u2019ve collected to enjoy in your old age. Get busy with life\u2019s purpose, toss aside empty hopes, get active in your own rescue\u2014if you care for yourself at all\u2014and do it while you can.\u201d",
        )

    # Check if some quote sources are correct
    def test_quote_sources(self):
        self.assertEqual(
            self.data["January 1"]["quote_source"],
            "\u2014EPICTETUS, DISCOURSES, 2.5.4\u20135",
        )
        self.assertEqual(
            self.data["January 8"]["quote_source"],
            "\u2014SENECA, MORAL LETTERS, 74.12b\u201313",
        )
        self.assertEqual(
            self.data["January 21"]["quote_source"],
            "\u2014EPICTETUS, DISCOURSES, 4.6.34\u201335",
        )
        self.assertEqual(
            self.data["February 7"]["quote_source"],
            "\u2014SENECA, OEDIPUS, 992",
        )
        self.assertEqual(
            self.data["February 9"]["quote_source"],
            "\u2014MARCUS AURELIUS, MEDITATIONS, 6.52",
        )
        self.assertEqual(
            self.data["July 29"]["quote_source"],
            "\u2014SENECA, MORAL LETTERS, 111.2",
        )
        self.assertEqual(
            self.data["December 31"]["quote_source"],
            "\u2014MARCUS AURELIUS, MEDITATIONS, 3.14",
        )

    # Check if some explanations are correct
    def test_explanations(self):
        self.assertEqual(
            self.data["January 1"]["explanation"],
            "The single most important practice in Stoic philosophy is differentiating between what we can change and what we can\u2019t. What we have influence over and what we do not. A flight is delayed because of weather\u2014no amount of yelling at an airline representative will end a storm. No amount of wishing will make you taller or shorter or born in a different country. No matter how hard you try, you can\u2019t make someone like you. And on top of that, time spent hurling yourself at these immovable objects is time not spent on the things we can change. The recovery community practices something called the Serenity Prayer: \u201cGod, grant me the serenity to accept the things I cannot change, the courage to change the things I can, and the wisdom to know the difference.\u201d Addicts cannot change the abuse suffered in childhood. They cannot undo the choices they have made or the hurt they have caused. But they can change the future\u2014through the power they have in the present moment. As Epictetus said, they can control the choices they make right now. The same is true for us today. If we can focus on making clear what parts of our day are within our control and what parts are not, we will not only be happier, we will have a distinct advantage over other people who fail to realize they are fighting an unwinnable battle.",
        )
        self.assertEqual(
            self.data["January 8"]["explanation"],
            "What we consider to be harmless indulgences can easily become full-blown addictions. We start with coffee in the morning, and soon enough we can\u2019t start the day without it. We check our email because it\u2019s part of our job, and soon enough we feel the phantom buzz of the phone in our pocket every few seconds. Soon enough, these harmless habits are running our lives. The little compulsions and drives we have not only chip away at our freedom and sovereignty, they cloud our clarity. We think we\u2019re in control\u2014but are we really? As one addict put it, addiction is when we\u2019ve \u201clost the freedom to abstain.\u201d Let us reclaim that freedom. What that addiction is for you can vary: Soda? Drugs? Complaining? Gossip? The Internet? Biting your nails? But you must reclaim the ability to abstain because within it is your clarity and self-control.",
        )
        self.assertEqual(
            self.data["January 21"]["explanation"],
            "Many successful people have a morning ritual. For some, it\u2019s meditation. For others, it\u2019s exercise. For many, it\u2019s journaling\u2014just a few pages where they write down their thoughts, fears, hopes. In these cases, the point is not so much the activity itself as it is the ritualized reflection. The idea is to take some time to look inward and examine. Taking that time is what Stoics advocated more than almost anything else. We don\u2019t know whether Marcus Aurelius wrote his Meditations in the morning or at night, but we know he carved out moments of quiet alone time\u2014and that he wrote for himself, not for anyone else. If you\u2019re looking for a place to start your own ritual, you could do worse than Marcus\u2019s example and Epictetus\u2019s checklist. Every day, starting today, ask yourself these same tough questions. Let philosophy and hard work guide you to better answers, one morning at a time, over the course of a life.",
        )
        self.assertEqual(
            self.data["February 7"]["explanation"],
            "\u201cOnly the paranoid survive,\u201d Andy Grove, a former CEO of Intel, famously said. It might be true. But we also know that the paranoid often destroy themselves quicker and more spectacularly than any enemy. Seneca, with his access and insight into the most powerful elite in Rome, would have seen this dynamic play out quite vividly. Nero, the student whose excesses Seneca tried to curb, killed not only his own mother and wife but eventually turned on Seneca, his mentor, too. The combination of power, fear, and mania can be deadly. The leader, convinced that he might be betrayed, acts first and betrays others first. Afraid that he\u2019s not well liked, he works so hard to get others to like him that it has the opposite effect. Convinced of mismanagement, he micromanages and becomes the source of the mismanagement. And on and on\u2014the things we fear or dread, we blindly inflict on ourselves. The next time you are afraid of some supposedly disastrous outcome, remember that if you don\u2019t control your impulses, if you lose your self-control, you may be the very source of the disaster you so fear. It has happened to smarter and more powerful and more successful people. It can happen to us too.",
        )
        self.assertEqual(
            self.data["February 9"]["explanation"],
            "Here\u2019s a funny exercise: think about all the upsetting things you don\u2019t know about\u2014stuff people might have said about you behind your back, mistakes you might have made that never came to your attention, things you dropped or lost without even realizing it. What\u2019s your reaction? You don\u2019t have one because you don\u2019t know about it. In other words, it is possible to hold no opinion about a negative thing. You just need to cultivate that power instead of wielding it accidentally. Especially when having an opinion is likely to make us aggravated. Practice the ability of having absolutely no thoughts about something\u2014act as if you had no idea it ever occurred. Or that you\u2019ve never heard of it before. Let it become irrelevant or nonexistent to you. It\u2019ll be a lot less powerful this way.",
        )
        self.assertEqual(
            self.data["July 29"]["explanation"],
            "What is \u201ca cure for the self\u201d? Perhaps Seneca means that, through nature and nurture, we develop a unique set of characteristics\u2014some positive and some negative. When those negative characteristics begin to have consequences in our lives, some of us turn to therapy, psychoanalysis, or the help of a support group. The point? To cure certain selfish, destructive parts of ourselves. But of all the avenues for curing our negative characteristics, philosophy has existed the longest and helped the most people. It is concerned not just with mitigating the effects of a mental illness or a neurosis, but it is designed to encourage human flourishing. It\u2019s designed to help you live the Good Life. Don\u2019t you deserve to flourish? Wouldn\u2019t you like to be great of soul, filled with confidence, and invincible to external events? Wouldn\u2019t you like to be like the proverbial onion, packed with layers of greatness? Then practice your philosophy.",
        )
        self.assertEqual(
            self.data["December 31"]["explanation"],
            "The purpose of all our reading and studying is to aid us in the pursuit of the good life (and death). At some point, we must put our books aside and take action. So that, as Seneca put it, the \u201cwords become works.\u201d There is an old saying that a \u201cscholar made is a soldier spoiled.\u201d We want to be both scholars and soldiers\u2014soldiers in the good fight. That\u2019s what\u2019s next for you. Move forward, move onward. Another book isn\u2019t the answer. The right choices and decisions are. Who knows how much time you have left, or what awaits us tomorrow?",
        )


if __name__ == "__main__":
    unittest.main()
