# Tarok Card Game

**/start**  - Start a new Tarok game
**/join**   - Join an existing game ( optionally pass Game-ID )
**/play**   - Play a card ( pass a card selection )
**/fold**   - End game ( optionally pass Game-ID )
**/hand**   - Get a player's hand ( optionally pass Game-ID )
**/state**  - Get the game state ( optionally pass Game-ID )
**/winner** - Get the winner of a game ( optionally pass Game-ID )
**/list**   - List available games with players
**/help**   - This help string

The Tarok card game, adapted for 2 players, using a 78 card deck:
- Play the same suited card as your opponent, else play a trump card ( cards numbered I to XXI & the Fool ).
- If a player cannot make a move they lose the game.
- The player with the most valued cards, wins the round.

# Service unit

[Unit]
Description=Monitor DMs Script
After=network.target

[Service]
ExecStart=/usr/bin/python /opt/monitor_DMs.py --priKeyEnvKey NOSTR_PRI_TAROK
Restart=always
RestartSec=5
WorkingDirectory=/opt
User=<your_user>
Group=<your_group>
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

