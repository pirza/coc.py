# this example assumes you have discord.py > v1.0.0
# installed via `python -m pip install -U discord.py`
# for more info on using discord.py, see the docs at:
# https://discordpy.readthedocs.io/en/latest
import discord
from discord.ext import commands

import coc
import traceback

bot = commands.Bot(command_prefix="?")
coc_client = coc.login("email", "password", key_count=5, key_names="My funky name!", client=coc.EventsClient,)
INFO_CHANNEL_ID = 123456678  # some discord channel ID


@coc_client.event
async def on_clan_member_join(member, clan):
    await bot.get_channel(INFO_CHANNEL_ID).send(
        "{0.name} ({0.tag}) just " "joined our clan {1.name} " "({1.tag})!".format(member, clan)
    )


@coc_client.event
async def on_player_name_change(old_name, new_name, player):
    await bot.get_channel(INFO_CHANNEL_ID).send(
        "Name Change! {0} is now called {1} " "(his tag is {2.tag})".format(old_name, new_name, player)
    )


@coc_client.event
async def on_event_error(event_name, exception, *args, **kwargs):
    if isinstance(exception, coc.PrivateWarLog):
        return  # lets ignore private war log errors
    print(
        "Uh oh! Something went wrong in %s event... printing traceback for you.", event_name,
    )
    traceback.print_exc()


@bot.command()
async def player_heroes(ctx, player_tag):
    if not utils.is_valid_tag(player_tag):
        await ctx.send("You didn't give me a proper tag!")
        return

    player = await coc_client.get_player(player_tag)

    to_send = ""
    for hero in player.heroes:
        to_send += "{}: Lv{}/{}".format(str(hero), hero.level, hero.max_level)

    await ctx.send(to_send)


@bot.command()
async def clan_info(ctx, clan_tag):
    if not utils.is_valid_tag(clan_tag):
        await ctx.send("You didn't give me a proper tag!")
        return

    clan = await coc_client.get_clan(clan_tag)

    if clan.public_war_log is False:
        log = "Private"
    else:
        log = "Public"
    e = discord.Embed(colour=discord.Colour.green())
    e.set_thumbnail(url=clan.badge.url)
    e.add_field(name="Clan Name", value=f"{clan.name}({clan.tag})\n[Open in game]({clan.share_link})", inline=False)
    e.add_field(name="Clan Level", value=clan.level, inline=False)
    e.add_field(name="Description", value=clan.description, inline=False)
    e.add_field(name="Leader", value=clan.get_member_by(role=coc.Role.leader), inline=False)
    e.add_field(name="Clan Type", value=clan.type, inline=False)
    e.add_field(name="Location", value=clan.location, inline=False)
    e.add_field(name="Total Clan Trophies", value=clan.points, inline=False)
    e.add_field(name="Total Clan Versus Trophies", value=clan.versus_points, inline=False)
    e.add_field(name="WarLog Type", value=log, inline=False)
    e.add_field(name="Required Trophies", value=clan.required_trophies, inline=False)
    e.add_field(name="War Win Streak", value=clan.war_win_streak, inline=False)
    e.add_field(name="War Frequency", value=clan.war_frequency, inline=False)
    e.add_field(name="Clan War League Rank", value=clan.war_league, inline=False)
    e.add_field(name="Clan Labels", value="\n".join(label.name for label in clan.labels), inline=False)
    e.add_field(name="Member Count", value=f"{clan.member_count}/50", inline=False)
    e.add_field(name="Clan Record", value=f"Won - {clan.war_wins}\nLost - {clan.war_losses}\n Draw - {clan.war_ties}", inline=False)
    await ctx.send(embed=e)


@bot.command()
async def clan_member(ctx, clan_tag):
    if not utils.is_valid_tag(clan_tag):
        await ctx.send("You didn't give me a proper tag!")
        return

    clan = await coc_client.get_clan(clan_tag)

    member = ""
    for i, a in enumerate(clan.members, start=1):
        member += f'`{i}.` {a.name}\n'
    embed = discord.Embed(colour=discord.Colour.red(), title=f'Members of {clan.name}', description=member)
    embed.set_thumbnail(url=clan.badge.url)
    embed.set_footer(text=f'Total Members - {clan.member_count)}/50')
    await ctx.send(embed=embed)


@bot.command()
async def current_war_status(ctx, clan_tag):
    if not utils.is_valid_tag(clan_tag):
        await ctx.send("You didn't give me a proper tag!")
        return

    e = discord.Embed(colour=discord.Colour.blue())

    try:
        war = await coc_client.get_current_war(clan_tag)
    except coc.PrivateWarLog:
        return await ctx.send("Clan has a private war log!")

    e.add_field(name=war.clan.name, value=war.clan.tag)

    e.add_field(name="War State:", value=war.state, inline=False)

    if war.end_time:  # if state is notInWar we will get errors

        hours, remainder = divmod(int(war.end_time.seconds_until), 3600)
        minutes, seconds = divmod(remainder, 60)

        e.add_field(
            name="Opponent:", value=f"{war.opponent.name}\n" f"{war.opponent.tag}", inline=False,
        )
        e.add_field(
            name="War End Time:", value=f"{hours} hours {minutes} minutes {seconds} seconds", inline=False,
        )

    await ctx.send(embed=e)


coc_client.add_clan_update(
    "clan_tag", retry_interval=600
)  # add clan updates for that clan tag, searching for changes every 10min
coc_client.start_updates()  # start looking for updates

bot.run("bot token")
