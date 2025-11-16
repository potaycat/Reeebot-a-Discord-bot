import discord
from discord import app_commands
from discord.ext import commands
from poke_env import (
    Player,
    ShowdownServerConfiguration,
    AccountConfiguration,
    ServerConfiguration,
)
from poke_env.player import SimpleHeuristicsPlayer
from poke_env.player.battle_order import SingleBattleOrder
from poke_env.battle.battle import Battle
from poke_env.battle.move import Move
from poke_env.battle.pokemon import Pokemon

import asyncio
import logging
from typing import Optional
import os

# Configure logging for poke-env
logger = logging.getLogger(__name__)


class DiscordPlayer(Player):
    """Custom Player that gets move choices from Discord interactions"""

    def __init__(
        self,
        interaction: discord.Interaction,
        bot_loop: asyncio.AbstractEventLoop,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.bot_loop = bot_loop  # Store Discord bot's event loop
        self.move_choice = None
        self.choice_event = asyncio.Event()
        self.battle_message = None  # Store the battle message to edit it

        # Track previous turn state
        self.prev_player_hp = {}
        self.prev_opponent_hp = {}
        self.prev_player_status = {}
        self.prev_opponent_status = {}
        self.prev_player_active = None
        self.prev_opponent_active = None
        self.last_player_move = None
        self.last_opponent_move = None
        self.last_player_switch = None

    async def choose_move(self, battle: Battle):
        """Extended choose_move that displays Discord UI for move selection"""
        try:
            # Reset choice for new turn
            self.move_choice = None
            self.choice_event.clear()

            # Get available moves and switches
            available_moves = [move for move in battle.available_moves if move.id]
            available_switches = [switch for switch in battle.available_switches]

            if not available_moves and not available_switches:
                # Force a random move if no choices available
                logger.warning("No moves or switches available, choosing random")
                return self.choose_random_move(battle)

            # Create view with buttons for moves and dropdown for switches
            view = BattleView(self, battle, available_moves, available_switches)

            # Format battle state message
            embed = self._create_battle_embed(
                battle, available_moves, available_switches
            )

            # Generate last turn summary
            last_turn_summary = self._generate_last_turn_summary(battle)

            # Send or edit the message with buttons - schedule on Discord's event loop
            try:
                if self.battle_message is None:
                    # First turn - edit the "Starting battle..." message
                    future = asyncio.run_coroutine_threadsafe(
                        self.battle_message.edit(
                            content=last_turn_summary,
                            embed=embed,
                            view=view,
                        ),
                        self.bot_loop,
                    )
                    future.result(timeout=10.0)
                else:
                    # Subsequent turns - edit existing message
                    future = asyncio.run_coroutine_threadsafe(
                        self.battle_message.edit(
                            content=last_turn_summary,
                            embed=embed,
                            view=view,
                        ),
                        self.bot_loop,
                    )
                    future.result(timeout=10.0)
            except Exception as e:
                logger.error(f"Error sending battle UI: {e}", exc_info=True)
                return self.choose_random_move(battle)

            await self.choice_event.wait()

            # Store the move for next turn's summary
            if isinstance(self.move_choice, Move):
                self.last_player_move = self.move_choice
                self.last_player_switch = None
            elif isinstance(self.move_choice, Pokemon):
                # Player switched Pokemon
                self.last_player_switch = self.move_choice
                self.last_player_move = None
            else:
                self.last_player_move = None
                self.last_player_switch = None

            # Store current HP and status for next turn comparison
            if battle.active_pokemon:
                player_species = str(battle.active_pokemon.species)
                self.prev_player_hp[player_species] = battle.active_pokemon.current_hp
                self.prev_player_status[player_species] = battle.active_pokemon.status
                self.prev_player_active = player_species
            if battle.opponent_active_pokemon:
                opp_species = str(battle.opponent_active_pokemon.species)
                self.prev_opponent_hp[opp_species] = (
                    battle.opponent_active_pokemon.current_hp
                )
                self.prev_opponent_status[opp_species] = (
                    battle.opponent_active_pokemon.status
                )
                self.prev_opponent_active = opp_species

            # Ensure move_choice is not None before wrapping
            if self.move_choice is None:
                logger.warning("Move choice is None, choosing random move")
                return self.choose_random_move(battle)

            # Wrap the choice in SingleBattleOrder
            return SingleBattleOrder(self.move_choice)
        except Exception as e:
            logger.error(f"Error in choose_move: {e}", exc_info=True)
            # Fallback to random move on any error
            return self.choose_random_move(battle)

    def _generate_last_turn_summary(self, battle: Battle) -> str:
        """Generate a summary of what happened in the last turn"""
        if battle.turn == 1:
            return "**Turn 1** - Battle Start!"

        summary_parts = []
        summary_parts.append(f"**Turn {battle.turn}**")

        # Check if player switched Pokemon
        if self.last_player_switch:
            switch_species = str(self.last_player_switch.species)
            summary_parts.append(f"🔄 You switched to **{switch_species}**")
        # Player's last move and damage dealt
        elif self.last_player_move:
            move_name = str(self.last_player_move.id).replace("_", " ").title()
            summary_parts.append(f"🔹 You used **{move_name}**")

            # Calculate damage dealt to opponent
            if battle.opponent_active_pokemon:
                opp_species = str(battle.opponent_active_pokemon.species)
                prev_hp = self.prev_opponent_hp.get(opp_species)
                current_hp = battle.opponent_active_pokemon.current_hp

                if prev_hp is not None and prev_hp > current_hp:
                    hp_loss = prev_hp - current_hp
                    summary_parts.append(
                        f"   → Dealt **{hp_loss}** HP damage to opponent!"
                    )

                # Check if opponent fainted
                if prev_hp is not None and prev_hp > 0 and current_hp == 0:
                    summary_parts.append(f"   💀 **Opponent's {opp_species} fainted!**")

                # Check for status infliction on opponent
                prev_status = self.prev_opponent_status.get(opp_species)
                current_status = battle.opponent_active_pokemon.status
                if prev_status != current_status and current_status is not None:
                    status_name = current_status.name
                    summary_parts.append(
                        f"   🌀 Inflicted **{status_name}** on opponent!"
                    )

        # Check if opponent switched Pokemon
        if battle.opponent_active_pokemon:
            current_opp_species = str(battle.opponent_active_pokemon.species)
            if (
                self.prev_opponent_active
                and self.prev_opponent_active != current_opp_species
            ):
                # Opponent switched (only show if they didn't faint)
                prev_hp = self.prev_opponent_hp.get(self.prev_opponent_active, 0)
                if prev_hp > 0:
                    summary_parts.append(
                        f"🔄 Opponent switched to **{current_opp_species}**"
                    )

        # Opponent's last move and damage dealt
        if battle.opponent_active_pokemon:
            # Try to get opponent's last move from their active pokemon
            opp_mon = battle.opponent_active_pokemon
            if hasattr(opp_mon, "moves") and opp_mon.moves:
                # Get the most recently used move
                moves_list = list(opp_mon.moves.values())
                if moves_list:
                    last_opp_move = moves_list[-1]
                    move_name = (
                        str(last_opp_move.id).replace("_", " ").title()
                        if last_opp_move.id
                        else "Unknown"
                    )
                    summary_parts.append(f"🔸 Opponent used **{move_name}**")

                    # Calculate damage dealt to player
                    if battle.active_pokemon:
                        player_species = str(battle.active_pokemon.species)
                        prev_hp = self.prev_player_hp.get(player_species)
                        current_hp = battle.active_pokemon.current_hp

                        if prev_hp is not None and prev_hp > current_hp:
                            hp_loss = prev_hp - current_hp
                            summary_parts.append(
                                f"   → You took **{hp_loss}** HP damage!"
                            )

                        # Check for status infliction on player
                        prev_status = self.prev_player_status.get(player_species)
                        current_status = battle.active_pokemon.status
                        if prev_status != current_status and current_status is not None:
                            status_name = current_status.name
                            if status_name == "FNT":
                                summary_parts.append(
                                    f"   💀 **Your {player_species} fainted!**"
                                )
                            else:
                                summary_parts.append(
                                    f"   🌀 You were inflicted with **{status_name}**!"
                                )

        if len(summary_parts) == 1:  # Only has turn number
            summary_parts.append("Something happened.")

        summary_parts.append(f"**Turn {battle.turn+1}**:")

        return "\n".join(summary_parts)

    def _create_battle_embed(
        self, battle: Battle, moves: list, switches: list
    ) -> discord.Embed:
        """Create an embed showing the current battle state"""
        try:
            embed = discord.Embed(title="⚔️ Pokemon Battle!", color=discord.Color.red())

            # Player's active Pokemon
            player_mon = battle.active_pokemon
            if player_mon:
                hp_percent = (
                    (player_mon.current_hp / player_mon.max_hp * 100)
                    if player_mon.max_hp
                    else 0
                )
                species = str(player_mon.species) if player_mon.species else "Unknown"
                status = player_mon.status.name if player_mon.status else "Healthy"
                item = str(player_mon.item).replace("_", " ").title() if player_mon.item else "None"
                ability = str(player_mon.ability).replace("_", " ").title() if player_mon.ability else "Unknown"
                speed = player_mon.speed if hasattr(player_mon, 'speed') and player_mon.speed else "Unknown"
                embed.add_field(
                    name=f"You",
                    value=f"{species.upper()}\nHP: {player_mon.current_hp}/{player_mon.max_hp} ({hp_percent:.1f}%)\n"
                    f"Status: {status}\nAbility: {ability}\nItem: {item}",
                    inline=True,
                )

            # Opponent's active Pokemon
            opp_mon = battle.opponent_active_pokemon
            if opp_mon:
                hp_percent = (
                    (opp_mon.current_hp / opp_mon.max_hp * 100) if opp_mon.max_hp else 0
                )
                species = str(opp_mon.species) if opp_mon.species else "Unknown"
                status = opp_mon.status.name if opp_mon.status else "Healthy"
                item = str(opp_mon.item).replace("_", " ").title() if opp_mon.item else "None"
                ability = str(opp_mon.ability).replace("_", " ").title() if opp_mon.ability else "Unknown"
                speed = opp_mon.speed if hasattr(opp_mon, 'speed') and opp_mon.speed else "Unknown"
                embed.add_field(
                    name=f"Opponent",
                    value=f"{species.upper()}\nHP: {opp_mon.current_hp}/{opp_mon.max_hp} ({hp_percent:.1f}%)\n"
                    f"Status: {status}\nAbility: {ability}\nItem: {item}",
                    inline=True,
                )

            return embed
        except Exception as e:
            logger.error(f"Error creating battle embed: {e}", exc_info=True)
            # Return a minimal embed on error
            embed = discord.Embed(title="⚔️ Pokemon Battle!", color=discord.Color.red())
            embed.add_field(
                name="Error", value="Failed to load battle state", inline=False
            )
            return embed


class BattleView(discord.ui.View):
    """Discord UI View with buttons for moves and dropdown for switches"""

    def __init__(
        self, player: DiscordPlayer, battle: Battle, moves: list, switches: list
    ):
        super().__init__(timeout=350.0)  # will lose before timeout
        self.player = player
        self.battle = battle

        # Add buttons for each available move
        for i, move in enumerate(moves[:4]):  # Max 4 moves
            button = MoveButton(move, i)
            self.add_item(button)

        # Add dropdown for switching Pokemon
        if switches:
            dropdown = SwitchDropdown(switches)
            self.add_item(dropdown)

    async def on_timeout(self):
        pass


class MoveButton(discord.ui.Button):
    """Button for selecting a move"""

    def __init__(self, move: Move, index: int):
        self.move = move
        # Choose button style based on move type/power
        style = discord.ButtonStyle.primary
        # if move.base_power >= 100:
        #     style = discord.ButtonStyle.danger
        # elif move.base_power >= 50:
        #     style = discord.ButtonStyle.success

        # Ensure move.id is not None
        move_name = (
            str(move.id).replace("_", " ").title() if move.id else f"Move {index+1}"
        )

        super().__init__(
            label=move_name,
            style=style,
            custom_id=f"move_{index}",
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle move button click"""
        try:
            view: BattleView = self.view

            # Set the player's choice
            view.player.move_choice = self.move
            view.player.choice_event.set()

            # Disable all buttons
            for item in view.children:
                item.disabled = True

            move_name = (
                str(self.move.id).replace("_", " ").title()
                if self.move.id
                else "Unknown Move"
            )

            # Get existing message content and append the move
            existing_content = interaction.message.content
            new_content = f"{existing_content}\n🔹 Using **{move_name}**..."

            await interaction.response.edit_message(
                content=new_content,
                view=view,
            )
        except Exception as e:
            logger.error(f"Error in MoveButton callback: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Error processing move selection", ephemeral=True
            )


class SwitchDropdown(discord.ui.Select):
    """Dropdown for selecting a Pokemon to switch to"""

    def __init__(self, switches: list):
        self.switches = switches

        options = []
        for pokemon in switches:
            try:
                hp_percent = (
                    (pokemon.current_hp / pokemon.max_hp * 100) if pokemon.max_hp else 0
                )
                species = str(pokemon.species) if pokemon.species else "Unknown"
                options.append(
                    discord.SelectOption(
                        label=species,
                        description=f"HP: {pokemon.current_hp}/{pokemon.max_hp} ({hp_percent:.0f}%)",
                        value=str(switches.index(pokemon)),
                    )
                )
            except Exception as e:
                logger.error(
                    f"Error creating switch option for pokemon: {e}", exc_info=True
                )
                # Add a fallback option
                options.append(
                    discord.SelectOption(
                        label="Unknown Pokemon",
                        description="Error loading pokemon data",
                        value=str(switches.index(pokemon)),
                    )
                )

        super().__init__(
            placeholder="Switch Pokemon...", options=options, custom_id="switch_pokemon"
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle Pokemon switch selection"""
        try:
            view: BattleView = self.view

            # Get selected Pokemon
            selected_index = int(self.values[0])
            selected_pokemon = self.switches[selected_index]

            # Set the player's choice to switch
            view.player.move_choice = selected_pokemon
            view.player.choice_event.set()

            # Disable all buttons
            for item in view.children:
                item.disabled = True

            species = (
                str(selected_pokemon.species)
                if selected_pokemon.species
                else "Unknown Pokemon"
            )

            # Get existing message content and append the move
            existing_content = interaction.message.content
            new_content = f"{existing_content}\n🔄 Switching to **{species}**..."

            await interaction.response.edit_message(
                content=new_content,
                view=view,
            )
        except Exception as e:
            logger.error(f"Error in SwitchDropdown callback: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ Error processing switch selection", ephemeral=True
            )


class PokemonBattle(commands.Cog, name="Pokemon Battle"):
    """
    Pokemon battling using poke-env
    """

    def __init__(self, bot):
        self.bot = bot
        self.active_battles = {}  # Store active battles by user ID

    @app_commands.command(name="battle", description="Start a Pokemon battle!")
    async def battle(
        self,
        interaction: discord.Interaction,
    ):
        """Start a Pokemon battle against a bot"""

        # Check if user already has an active battle
        if interaction.user.id in self.active_battles:
            await interaction.response.send_message(
                "You already have an active battle! Finish it first.", ephemeral=True
            )
            return

        asyncio.create_task(interaction.response.defer())

        try:
            # Create player and opponent
            player_name = f"a{str(interaction.user.id)[-17:]}"
            opponent_name = f"b{str(interaction.user.id)[-17:]}"

            server_config = ServerConfiguration(
                "ws://play.pschina.one/showdown/websocket",
                "https://play.pokemonshowdown.com/~~china/action.php",
            )

            # Get the Discord bot's event loop
            bot_loop = asyncio.get_event_loop()

            player = DiscordPlayer(
                interaction=interaction,
                bot_loop=bot_loop,  # Pass the bot's event loop
                battle_format="gen5randombattle",
                max_concurrent_battles=1,
                start_timer_on_battle_start=True,
                server_configuration=server_config,
                account_configuration=AccountConfiguration(player_name, "_"),
                log_level=logging.WARNING,
            )

            opponent = SimpleHeuristicsPlayer(
                battle_format="gen5randombattle",
                max_concurrent_battles=1,
                start_timer_on_battle_start=True,
                server_configuration=server_config,
                account_configuration=AccountConfiguration(opponent_name, "_"),
                log_level=logging.WARNING,
            )

            # Store battle
            self.active_battles[interaction.user.id] = (player, opponent)

            # Send starting message and store it for later editing
            starting_message = await interaction.followup.send(
                "🎮 Starting Pokemon battle...", wait=True
            )
            player.battle_message = starting_message

            # Start battle
            try:
                await player.battle_against(opponent, n_battles=1)

                # Battle finished, show result
                battle = list(player.battles.values())[0]
                if battle.won:
                    result_msg = "🎉 You won the battle!"
                else:
                    result_msg = "😢 You lost the battle!"

                await starting_message.edit(content=result_msg, view=None)

            except ConnectionRefusedError as e:
                logger.error(f"Connection refused: {e}")
                await interaction.followup.send(
                    "❌ **Pokemon Showdown server is not running!**\n"
                    "Please start a local server:\n"
                    "1. Install Node.js\n"
                    "2. Clone https://github.com/smogon/pokemon-showdown\n"
                    "3. Run: `node pokemon-showdown start --no-security`\n"
                    "See `POKEMON_BATTLE_SETUP.md` for details."
                )
            except Exception as e:
                logger.error(f"Battle error: {e}", exc_info=True)
                await interaction.followup.send(f"❌ Battle error: {str(e)}")

            # Clean up
            if interaction.user.id in self.active_battles:
                del self.active_battles[interaction.user.id]

        except Exception as e:
            logger.error(f"Error starting battle: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error starting battle: {str(e)}")
            if interaction.user.id in self.active_battles:
                del self.active_battles[interaction.user.id]


async def setup(bot):
    await bot.add_cog(PokemonBattle(bot))
