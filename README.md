# Pretty Zaney (and zippy) Software<br>by BlooberryMoth

PZ(az)S (pronounced "pizzazz") is by far my oldest and most worked on project, as well as my most loved.<br>
This originated as a gimick bot that my friends and I used only to track a dumb game we played: see who can say "first" first every day.<br>
Now, years later, it's grown into my most favorite project I've ever worked on. I've added so much more depth to it and plan to keep adding more for as long as I have ideas. (And as long as it keeps breaking :P)

# Features:
## Starboard!
The classic Starboard! How could I not include this?<br>
What is it? It's essentially a server-wide pinned messages function, mostly used to save messages you and your friends love a lot<br>
Simply react to a message with a certain number of stars to put that message in to that "hall-of-fame" of sorts.<br>
You can enable it with `/starboard enable <channel> [minimum star count]`<br>
and disable it with `/starboard disable`<br>
<sub>Note: `<option>` means "required", and `[option]` means "optional"</sub><br><br>

Though this may be a classic feature, it is certainly unlike most others I've seen.<br>
I've always been a little annoyed at other Discord bots' version of the Starboard, as most do not include gifs, only images, and also won't include multiple images.
So I've taken the effort of ensuring that every* gif and image (and even sticker too!) gets saved by this Starboard.<br>
<sub>  *up to 4</sub><br><br>
Multiple images: (competition did not attempt to "star" this message)
<img width="604" height="496" alt="multi_image" src="https://github.com/user-attachments/assets/2df2a0fb-d2e8-4b4a-8e3e-ae309da4d96e"/><br>
Multiple gifs: (competition also did not attempt to "star" this message)
![multi_gif](https://github.com/user-attachments/assets/00dd1e54-de2c-4675-ae94-63a960d917e1)
<br><br><br>

## Message reactions!
Ever wanted automated reactions to your messages? Well now you can have them!<br>
Using `/reactions` opens up a dialogue that allows you to set up to 10 emojis to be automatically added to your messages.<br>
You can choose what emojis react to what messages and even set it to only react in certain servers or channels.<br>
If you're a server owner and think this could be abused, you can turn off the "Add Reactions" permission on the Bot's role.<br><br>

## Auto user roles!
Another classic feature that allows users to give themselves roles by reacting to a message.<br>
Simply use `/autorole` and a dialogue will open that will allow you to make up to 10 different "auto role" messages, with up to 10 roles per message.<br>
<sub>Note: The maximum of 10 isn't hard-set. If enough people want I can change it to be any number.</sub><br><br>

## Games!
That's right, folks: the original reason I made this.<br>
So far there's only one game, First, but I plan on adding more as time goes on. I don't have any plans of future games, but I plan on planning future games :P<br>

### First:
To play, simply run the command `/first start [channel] [timezone] [start_date]`, and every day at midnight say "first" to win!<br>
Score is kept track and resets at the beginning of every month, and the player with the highest score will "win" that month.<br>
Rank is decided by who has the most wins, and then who has the most points that month. (So someone with 1 point but 3 wins will be higher rank than someone with 15 points and 1 win)<br><br>

As far as I'm aware, the code works with multiple people trying to say "first" first, and I haven't seen any issues with it keeping track of what messages are sent in what order.<br>
If you decide to set a starting date with the command it will gather all messages in the channel from when you specified and calculate who's won those days since then. (see /commands/first.py: build_statistics())<br>
You can see your score, as well as everyone else's, with `/first rank [@user]`. This command will also show a leaderboard with everyone's scores for that month.
<br><br><br>


# How it works:
Originally, this didn't even have commands to control anything about how it kept track of "first"; There was only one command to see how many times you had won.<br>
Now, I've ..."come up"... with ..."my own"... system for handling all the commands I've added, and made it extremely easy to add new ones.<br><br>

<ins>WARNING: TECHNICAL</ins><br>
Over the years I've made improvements on how the code handle's multiple commands, and how it handles executing them, but throughout those years the fundamentals have stayed exactly the same<br>

### Original:
```
Init (startup) ┓     This would gather all of the command files     ┃  Each command file was formatted as at least this:
┏━━━━━━━━━━━━━━┛     Into one dictionary that it could look up      ┃
┃                                                                   ┃  rank.py:
for file in os.listdir('./commands'):                               ┃    permission = 0
  if file.endswith('.py'):                                          ┃    aliases = [
    file = file.removesuffix('.py')                                 ┃      'rank',
    module = importlib.import_module(f'commands.{file}')            ┃      'r',
    commands[file] = {"aliases": module.aliases, "module": module}  ┃      'score'
                                                                    ┃    ]
@on_message event from Discord ┓                                    ┃    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                                    ┃  ┏ async def execute(args, message: discord.Message): ...
┃                                                                   ┃  ┃
if message.content.startswith(prefix):                              ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  permission = User's permission level                                 ┃
  alias, *args = message.content.removeprefix(prefix).split(' ')     
  for command in commands:                                             ┃
    if alias in commands[command]['aliases']:                        
      module = commands[command]['module']                             ┃
      if permission >= module.permission                               
        await module.execute(args, message)━━  ━━  ━━  ━━  ━━  ━━  ━━  ┛
```

### Now: (follow along in the files themselves!)
```
Main.py:

for folder in os.listdir('./events'):
  for file in os.listdir(f'./events/{folder}'):
    if file.startswith('@') and ...: module = importlib.import_module(f'events.{folder}.{file.removesuffix("py")}')

    vvvvvv
```
All the events are loaded by "abusing" Python's importing system. When you import a .py file in Python all the code is analyzed and all variables, methods, and decorations are loaded in to memory.
This means I can use the '@Client.event' decoration inside each '@event_name.py' file to load/import methods without using `from events.event import @event.py` for every event I might want to use.
This is a kind of abstraction that I think is extremely useful here, and can definitely be used elsewhere, but can be hazardous if used improperly.
```
    vvvvvv

events/on_message/@on_message.py:

for file in os.listdir('./events/on_message'):
  if not file.startswith('@') and file.endswith('.py'): # Ignoring this file itself
    module = importlib.import_module(f'events.on_message.{file.split(".py")[0]}')
    module.handle(message) # The "message" variable comes from the '@Client.event'

    vvvvvv
```
The '@on_message.py' file uses the same principle as object oriented game development where if you have multiple of the same object (e.g a enemy), instead of writing:
`class Enemy1: ...; class Enemy2: ...`<br>
and making them all move by writing: `Enemy1.move(); Enemy2.move()`<br>
You make one class and copy it into a list:
```
class Enemy: ...
all_enemies = [Enemy() for i in range(50)]
for enemy in all_enemies: enemy.move()
```
The event files themselves (non '@' files) are seperated by what purpose they serve, but each contains a `async def handle(...): ...` method that '@on_message.py' calls.<br>
After that, the 'handle_commands.py' file is essentially the same as the '@on_message' code from the original.<br>
The commands' aliases are still stored in a dictionary to save time and CPU power; Importing every command file any time someone says ".." at the beginning of their message is extremely impractical.