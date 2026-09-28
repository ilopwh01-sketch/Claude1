# TOEFL Voice Coach

A one-file web app for practicing TOEFL iBT **speaking** out loud. The browser reads each question aloud, listens to your answer through the microphone, turns it into text, and gives you instant feedback.

음성으로 TOEFL 스피킹을 연습하는 웹 앱입니다. 질문을 듣고, 마이크로 답하면 바로 피드백을 받을 수 있어요.

## How to open it

1. Download `index.html` (or clone this repo).
2. Open it in **Google Chrome** or **Microsoft Edge**. Voice recognition does not work in Safari or Firefox.
3. When the browser asks for microphone access, click **Allow**.

If the microphone doesn't work from a local file, serve the folder instead:

```bash
cd toefl-voice-coach
python3 -m http.server 8000
# then open http://localhost:8000 in Chrome
```

## Practice modes

| Mode | What you do | Feedback |
|---|---|---|
| **Listen & Repeat** | Hear a sentence once and repeat it exactly. 7 sentences per set, getting longer. | Word-by-word match: green = correct, red = missed. |
| **Take an Interview** | Answer 4 questions on one topic, 45 seconds each, no preparation time. | Word count, speaking speed (WPM), filler words, linking words, example check, 0–4 practice estimate, and a model answer you can listen to. |
| **Independent (Classic)** | 15 seconds to prepare, 45 seconds to give your opinion. | Same as the interview. |
| **Vocabulary** | Learn words the native way: hear the word in a sentence, guess the meaning, learn the phrases it goes with, say it, then use it in your own spoken sentence. | Pronunciation check, a check that you used the word, spaced-repetition reviews (Again / Hard / Good / Easy). |
| **My Progress** | See your past results (saved in your browser). | |

### Vocabulary decks

- **TOEFL academic words** (25): *significant, analyze, crucial, evidence, hypothesis, phenomenon…*, each with stress pattern, Korean meaning, natural collocations, and a conversational vs. academic alternative.
- **Phrasal verbs natives use** (16): *come up with, figure out, end up, turn out, put off…*, the everyday verbs that make speech sound native.

Each day you get up to 10 new words plus the words due for review. Words you rate "Good" come back after 1, 3, 7, 14, 30 and 60 days.

Every feedback card has a **Copy for Claude feedback** button. Paste the copied text into Claude to get grammar corrections, a rubric-based score, and an improved answer.

## Tips for a higher speaking score

- Answer the question in your first sentence.
- Give one reason and one **specific** personal example.
- Aim for 85–110 words in 45 seconds (110–150 words per minute).
- Use linking words: *because, for example, in addition, however, as a result*.
- Replace "um / uh" with a short silent pause.

The scores in this app are practice estimates, not official ETS scores.
