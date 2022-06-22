import pytz
from datetime import datetime
tz = pytz.timezone('UTC')
naive_time = datetime.now()
tz_time = tz.localize(naive_time)
london_tz = pytz.timezone('Europe/London')
london_time = tz_time.astimezone(london_tz)
print(london_time)



now = datetime.now()

day = now.strftime("%Y-%m-%d")
print(day)
hour = now.strftime("%H")
print(hour)

chubilee = {"2022-06-23-00":"welcome st0nerz w kiki and call ins",
        "2022-06-23-01":"sorting w/ tiger2 not live from prague",
        "2022-06-23-02":"Trombones w/ Andehhhh",
        "2022-06-23-03":"Jaanipäev w/meh",
        "2022-06-23-04":"Nonstop Fit - Trous first appearance",
        "2022-06-23-05":"faleme loop w/ cinnaron",
        "2022-06-23-06":"chunting with mavros",
        "2022-06-23-07":"Ok, I am Awake w/okiamevans",
        "2022-06-23-08":"Oscar Maldonados morning shift",
        "2022-06-23-09":"Early Dealer W/ Rival Dealer",
        "2022-06-23-10":"Early Dealer W/ Rival Dealer",
        "2022-06-23-11":"Yung Chunny Munny w Chunny Sunny ft. Peanuts MC",
        "2022-06-23-12":"bubbasee on the high seas",
        "2022-06-23-14":"DJ Dale - Jap Hip-Hop Special",
        "2022-06-23-15":"Relaxed Fit w large trou",
        "2022-06-23-16":"simple features w/ dj pauly c",
        "2022-06-23-17":"Turbobabe's Turbohour w/ Ginny",
        "2022-06-23-18":"HUGE DONKS w/ pixel",
        "2022-06-23-19":"Woi Workout with oscmal",
        "2022-06-23-20":"sort ur life out NOW w kiki",
        "2022-06-23-21":"NRG with P-Air",
        "2022-06-23-22":"Digital Rimming w/WoiKev",
        "2022-06-23-23":"Bowel Cleansers w/ number2",
        "2022-06-24-00":"🍍youanas sonic ananas🍍",
        "2022-06-24-01":"big al's wee drums",
        "2022-06-24-02":"GO AFTER",
        "2022-06-24-03":"LATE????????? PARTY"}

key = str(now.strftime("%Y-%m-%d-%H"))
print(key)
if key in chubilee:
    print(chubilee[key])