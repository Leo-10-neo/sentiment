from flask import Flask, render_template, request
from textblob import TextBlob
from PIL import Image
import io
import base64

app = Flask(__name__)

# --- Kannada Music & Movie Recommendations ---
recommendations = {
    "happy": {
        "songs": [
            ("old song – Karunada Tayi Sada Chinmayi", "https://youtu.be/ceKvyYE9G1s?si=6d9TsuOuYcQ9GwMF"),
            ("Kirik Party – Belageddu", "https://youtu.be/ebz20FHrT44?si=59kpR-lylh2RK7VI"),
            ("Love Mocktail – Neenu Neenu", "https://youtu.be/EGG14zJl420?si=x7ekI9olzYcnPR_I"),
            ("Mungaru Male – Anisuthide Yaako Indu", "https://youtu.be/nlsLKA6hlVQ?si=oufBmpkjaZoXZz0O"),
            ("Milana – Ninnindale", "https://youtu.be/-xmRjO2G05c?si=rkhuYAScBvrBI6lI"),
            ("Paramathma – College Gate", "https://youtu.be/sX4Bxks_VlI?si=yC9e9HahBNa-DwRQ"),
            ("Raajakumara – Chakravyuha", "https://youtu.be/T5V2kKqa8Wc?si=UAHMaXU6OYt-GJ38"),
            ("Kotigobba 2 – Kotigobba", "https://youtu.be/_qP1aywHgXE?si=wdj8EGLA8Gvml26R"),
            ("Ugramm – Ugramm Veeram", "https://youtu.be/hpWksXyK7OQ?si=5XEmeU3f-KXJljKf")
        ],
        "movies": [
            ("Su From So", "https://youtu.be/Fe11GLdTL5k?si=Y4s345xxZo_2_XJk"),
            ("Hostel Hudugaru Bekagiddare", "https://youtu.be/Q0sHtYB0umM?si=H4VixFbLFi1-VMzr"),
            ("Kirik Party", "https://youtu.be/IfvnbER_6sQ?si=GwGAgj4wygoRFKJI"),
            ("Bell Bottom", "https://youtu.be/0_W_PhKaQaY?si=z2pUj-HLPmNKnED6"),
            ("Gaalipata", "https://youtu.be/lCnQvZYVF7A?si=n2N6ViKh5L21IoY2")
        ]
    },

    "sad": {
        "songs": [
            ("Googly – Bisilu Kudreyondu", "https://youtu.be/N4GFIkcp5Wo?si=-aVsqJZ272n3O8dx"),
            ("Raajakumara – Saagaradha", "https://youtu.be/3WT2yGrWKoc?si=MmabY7Vfj70flJJJ"),
            ("Kavaludaari – Samshaya", "https://youtu.be/lfkDXLbIE7I?si=hEEjWNQIfAeoP92P"),
            ("Godhi Banna Sadharana Mykattu – Ee Sanjege", "https://youtu.be/41qxViSQgZk?si=TpfaQwvxKP_sS1Yy"),
            ("Love Mocktail – Kanna Haniyondhu", "https://youtu.be/7llPi3k-yQs?si=kblT-Q2bQnRdnkvF"),
            ("777 Charlie – The Hymn Of Dharma", "https://youtu.be/PubWT2Eg51w?si=IfV_qtBdUbOQ8kYE")
        ],
        "movies": [
            ("U Turn", "https://youtu.be/EAFtx938D8U?si=1t-kIDRyY5WuLlfc"),
            ("Kavaludaari", "https://youtu.be/5w1vgMoPMRA?si=iIiXiMpkMzXXoSTz"),
            ("Dia", "https://youtu.be/8GR-W0jGVak?si=92KrPAQ0yPIkxeTU"),
            ("Lucia", "https://youtu.be/pgIL2H-OdcA?si=lBOUuDm7jfhaCZrJ"),
            ("Love Mocktail", "https://youtu.be/up0NHLEq0nc?si=kj6d5uet86XPuGFS")
        ]
    },

    "neutral": {
        "songs": [
            ("KGF Chapter 1 – Salaam Rocky Bhai", "https://youtu.be/TnyWMhSqyjY?si=vfpd3v6EsbJXTTt1"),
            ("Tagaru – Tagaru Banthu Tagaru", "https://youtu.be/V3-Fd8wPuRA?si=BLNwEmjVMnO1JGVR"),
            ("Mundina Nildana – Innunu Bekagide", "https://youtu.be/fclPhO1FsOY?si=glGRcP7pKY2O4dl0"),
            ("HERO – Nenapina Hudugiye", "https://youtu.be/QCC9pkwvyaM?si=cpvhlJsiawi39Uwd"),
            ("KGF Chapter 2 – Toofan", "https://youtu.be/f2dTfaNm4n4?si=FVjG21CJhQNyu_kN")
        ],
        "movies": [
            ("KGF Chapter 1", "https://youtu.be/qXgF-iJ_ezE?si=yHdW0n9IvMQlGShZ"),
            ("Pailwaan", "https://youtu.be/POMumo3pS80?si=0_lrYB1PWCDwwwkk"),
            ("Roberrt", "https://youtu.be/IBPdSqV2gjs?si=xt8bxFVCGdNNZLEx"),
            ("James", "https://youtu.be/TPmBdjplUtY?si=gJGrQ2Xanke8-iEi"),
            ("KGF Chapter 2", "https://youtu.be/jQsE85cI384?si=J2HjzW4qmqUCu7ET")
        ]
    }
}

# ---------- SENTIMENT CHECK ----------
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        return "happy"
    elif polarity < -0.1:
        return "sad"
    elif -0.1 <= polarity <= 0.1:
        return "neutral"
    else:
        return "invalid"


@app.route("/", methods=["GET", "POST"])
def index():
    mood = None
    text = ""
    image_preview = None

    if request.method == "POST":
        text = request.form.get("text", "")
        mood = get_sentiment(text) if text else None

        # Image upload logic
        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            img = Image.open(image_file)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            image_preview = base64.b64encode(buf.getvalue()).decode("utf-8")

            # fallback (if no text)
            mood = mood or "happy"

        # VALIDATION: Only happy, sad, neutral allowed
        valid_moods = ["happy", "sad", "neutral"]
        if mood not in valid_moods:
            mood = "invalid"

    songs = recommendations.get(mood, {}).get("songs", [])
    movies = recommendations.get(mood, {}).get("movies", [])

    return render_template("index.html",
                           mood=mood,
                           text=text,
                           image=image_preview,
                           songs=songs,
                           movies=movies)


if __name__ == "__main__":
    app.run(debug=True)