import sqlite3
from sqlite3 import Error
DB='lingostu.db'

def f(w, e):
    conn = sqlite3.connect(DB) 
    cursor = conn.cursor()
    cursor.execute("INSERT INTO word_set (f_word, f_example) VALUES (?, ?)",(w, e))
    conn.commit()
    conn.close()


# ("garbage", "Sorry about the garbage cans blocking the driveway, I'll move them.")
# ("quiet","It's usually so quiet around here in the mornings.")
# ("rules","Are there any specific rules about using the pool?")
# ("property","Who owns the property at the end of the street?")
# ("fence","Our fence got damaged in the storm last night.")
# ("shared","The basement laundry is a shared space, isn't it?")
# ("courtesy","Just as a courtesy, I thought I'd let you know we're having people over tonight.")
# ("security","The security in our building is excellent.")
# ("meeting","Is the homeowners association meeting happening this Tuesday?")
# ("mail","Your mail got delivered to us by mistake.")
# ("package","There's a package for you in the lobby.")
# ("environment","We should do something about the environment, like organizing a clean-up.")
# ("lawn","Your lawn looks incredible! How do you keep it so green?")

f("recycling","I think we should start recycling, it's important for the environment.")
f("stomping","We can hear stomping from your apartment, it's a bit disturbing.")
f("clean up", "Could you please clean up after your dog in the garden?")
f("ceiling", "There's a water leak from my ceiling, I think it's coming from your apartment.")
f("wait","Could you wait to start your renovation until after 9 am?")
f("concern", "I understand your concern about the noise.")
f("tranquility","We moved here for the tranquility, it's so peaceful.")
f("upstairs","Every time the upstairs neighbors drop something, I half expect a bowling ball to come through the ceiling.")
f("downstairs","I think my downstairs neighbors might be vampires, they're only active after midnight!")

  

# f("nearby","There's a grocery store nearby.")
# f("safe","I feel really safe in this neighborhood.")


#,"Let's organize a playdate for our kids."