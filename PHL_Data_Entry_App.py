from datetime import date
import streamlit as st
import pandas as pd

def load_or_init_csv(label, session_key):
    uploaded_file = st.file_uploader(label, type=["csv"])
    if uploaded_file is not None:
        # Reload if new file or different filename from currently loaded
        if (session_key not in st.session_state or 
            st.session_state.get(f"{session_key}_filename", None) != uploaded_file.name):
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state[session_key] = df
                st.session_state[f"{session_key}_filename"] = uploaded_file.name
                st.success(f"'{uploaded_file.name}' loaded successfully.")
            except Exception as e:
                st.error(f"Error loading CSV: {e}")
    else:
        if session_key not in st.session_state:
            st.session_state[session_key] = pd.DataFrame()

    return st.session_state[session_key]

def Game_Result_List():
    Game_Result = [
    ('Win_Reg'),
    ('Win_OT'),
    ('Loss_Reg'),
    ('Loss_OT'),
    ]

    Game_Result = pd.DataFrame(Game_Result, columns=['Game_Result'])
    return Game_Result

def Team_Data_Entry_Form(current_date):
    st.title("Team Results Submission")

    # Access the shared dataframe in session state
    team_game_data = st.session_state.get('team_game_data', pd.DataFrame())
    PHL_Teams = st.session_state.get('PHL_Teams', pd.DataFrame())

    Game_Result = Game_Result_List()

    # Then proceed with your form inputs as before
    team_cols = st.columns(2)
    with team_cols[0]:
        team1_selection = st.selectbox("Choose Team #1", PHL_Teams['Team_Name'], index=None, placeholder="Please Select Team", key="Team1_Select")
        team1_code = PHL_Teams.loc[PHL_Teams['Team_Name'] == team1_selection, 'Team_Code'].values[0] if team1_selection else None
    with team_cols[1]:
        team2_selection = st.selectbox("Choose Team #2", PHL_Teams['Team_Name'], index=None, placeholder="Please Select Team", key="Team2_Select")
        team2_code = PHL_Teams.loc[PHL_Teams['Team_Name'] == team2_selection, 'Team_Code'].values[0] if team2_selection else None

    detail_cols = st.columns(2)
    with detail_cols[0]:
        Week = st.number_input("Week", min_value=1, max_value=52, step=1)
    with detail_cols[1]:
        Game_Number = st.number_input("Game Number", min_value=1, step=1)

    if team1_selection and team2_selection and Week and Game_Number:
        # Initialize session state keys if they don't exist
        for key in ['team1_result', 'team2_result', 'team1_shutout', 'team2_shutout']:
            if key not in st.session_state:
                st.session_state[key] = None if 'result' in key else "No"

        with st.form("game_stats_form"):
            st.markdown("### Enter Game Stats")
            stats_cols = st.columns(2)

            with stats_cols[0]:
                st.subheader(f"{team1_selection if team1_selection else 'Team #1'}")
                team1_goals = st.number_input("Goals", min_value=0, step=1, key="team1_goals")
                team1_assists = st.number_input("Assists", min_value=0, step=1, key="team1_assists")
                team1_shots = st.number_input("Shots", min_value=0, step=1, key="team1_shots")
                team1_saves = st.number_input("Saves", min_value=0, step=1, key="team1_saves")
                team1_result = st.selectbox(f"{team1_selection}'s Game Result", Game_Result, index=None, placeholder="Please Select Result", key="team1_result")

            with stats_cols[1]:
                st.subheader(f"{team2_selection if team2_selection else 'Team #2'}")
                team2_goals = st.number_input("Goals", min_value=0, step=1, key="team2_goals")
                team2_assists = st.number_input("Assists", min_value=0, step=1, key="team2_assists")
                team2_shots = st.number_input("Shots", min_value=0, step=1, key="team2_shots")
                team2_saves = st.number_input("Saves", min_value=0, step=1, key="team2_saves")
                # Outside the form: compute and update team2_result dynamically and display
                if st.session_state['team1_result'] == "Win_Reg":
                    st.session_state['team2_result'] = "Loss_Reg"
                elif st.session_state['team1_result'] == "Win_OT":
                    st.session_state['team2_result'] = "Loss_OT"
                elif st.session_state['team1_result'] == "Loss_Reg":
                    st.session_state['team2_result'] = "Win_Reg"
                elif st.session_state['team1_result'] == "Loss_OT":
                    st.session_state['team2_result'] = "Win_OT"
                elif st.session_state['team1_result'] == "Tie":
                    st.session_state['team2_result'] = "Tie"
                else:
                    st.session_state['team2_result'] = None

                # Show the automatic update message here to reflect changes immediately
                if team1_selection and team2_selection and st.session_state['team1_result']:
                    st.write(f"{team2_selection}'s result is automatically set to '{st.session_state['team2_result']}'.")


            submitted = st.form_submit_button("Submit")
        # Shutout logic (can be inside form or just after submit)
        if submitted:
            # Shutout logic
            if team1_goals == 0 and team2_goals > 0:
                st.session_state['team1_shutout'] = "Yes"
                st.session_state['team2_shutout'] = "No"
            elif team2_goals == 0 and team1_goals > 0:
                st.session_state['team2_shutout'] = "Yes"
                st.session_state['team1_shutout'] = "No"
            else:
                st.session_state['team1_shutout'] = "No"
                st.session_state['team2_shutout'] = "No"

            data = [
                {
                    "Team_Name": team1_selection,
                    "Team_Code": team1_code,
                    "Week": Week,
                    "Game_Number": Game_Number,
                    "Goals": team1_goals,
                    "Assists": team1_assists,
                    "Shots": team1_shots,
                    "Saves": team1_saves,
                    "Game_Result": st.session_state['team1_result'],
                    "Shoutout": st.session_state['team1_shutout'],
                    "Goals_Allowed": team2_goals,
                    "Assists_Allowed": team2_assists,
                    "Shots_Allowed": team2_shots,
                    "Saves_Allowed": team2_saves
                },
                {
                    "Team_Name": team2_selection,
                    "Team_Code": team2_code,
                    "Week": Week,
                    "Game_Number": Game_Number,
                    "Goals": team2_goals,
                    "Assists": team2_assists,
                    "Shots": team2_shots,
                    "Saves": team2_saves,
                    "Game_Result": st.session_state['team2_result'],
                    "Shoutout": st.session_state['team2_shutout'],
                    "Goals_Allowed": team1_goals,
                    "Assists_Allowed": team1_assists,
                    "Shots_Allowed": team1_shots,
                    "Saves_Allowed": team1_saves
                }
            ]
            new_df = pd.DataFrame(data)

            if team_game_data.empty:
                st.session_state['team_game_data'] = new_df
            else:
                st.session_state['team_game_data'] = pd.concat([team_game_data, new_df], ignore_index=True)

            st.dataframe(st.session_state['team_game_data'].style.hide(axis="index"))
            st.session_state['team_game_data'] = st.session_state['team_game_data'].reset_index(drop=True)

        # Prepare CSV data without index for download
        csv_data = st.session_state['team_game_data'].to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download Raw_Team_Data as CSV",
            data=csv_data,
            file_name=f'Raw_Team_Data-{current_date}.csv',
            mime='text/csv',
        )
            
    else:
        st.warning("Please select both teams, week, and game number to continue.")

def Player_Data_Entry_Form(current_date):
    st.title("Player Game Results Submission")

    # Access shared dataframes in session state
    PHL_Teams = st.session_state.get('PHL_Teams', pd.DataFrame())
    PHL_Roster = st.session_state.get('PHL_Roster', pd.DataFrame())
    team_game_data = st.session_state.get('team_game_data', pd.DataFrame())
    if 'player_game_data' not in st.session_state:
        st.session_state.player_game_data = pd.DataFrame()

    # Team selection inputs
    team_cols = st.columns(2)
    with team_cols[0]:
        player_team1_selection = st.selectbox(
            "Choose Team #1", PHL_Teams['Team_Name'], index=None,
            placeholder="Please Select Team", key="Team1_Player_Select"
        )
        player_team1_code = (
            PHL_Teams.loc[PHL_Teams['Team_Name'] == player_team1_selection, 'Team_Code'].values[0]
            if player_team1_selection else None
        )
    with team_cols[1]:
        player_team2_selection = st.selectbox(
            "Choose Team #2", PHL_Teams['Team_Name'], index=None,
            placeholder="Please Select Team", key="Team2_Player_Select"
        )
        player_team2_code = (
            PHL_Teams.loc[PHL_Teams['Team_Name'] == player_team2_selection, 'Team_Code'].values[0]
            if player_team2_selection else None
        )

    # Week and Game Number inputs
    detail_cols = st.columns(2)
    with detail_cols[0]:
        Week = st.number_input("Week", min_value=1, max_value=52, step=1, key="Player_Data_Week_Input")
    with detail_cols[1]:
        Game_Number = st.number_input("Game Number", min_value=1, step=1, key="Player_Data_Game_Number_Input")

    if player_team1_selection and player_team2_selection and Week and Game_Number:
        filter_condition_team1 = (
            (team_game_data['Team_Code'] == player_team1_code) &
            (team_game_data['Week'] == Week) &
            (team_game_data['Game_Number'] == Game_Number)
        )
        filter_condition_team2 = (
            (team_game_data['Team_Code'] == player_team2_code) &
            (team_game_data['Week'] == Week) &
            (team_game_data['Game_Number'] == Game_Number)
        )

        Team1_Game_Data = team_game_data.loc[filter_condition_team1]
        Team2_Game_Data = team_game_data.loc[filter_condition_team2]
        Team_1_Roster = PHL_Roster.loc[PHL_Roster['Team_Name'] == player_team1_selection].sort_values("Skater_Name")
        Team_2_Roster = PHL_Roster.loc[PHL_Roster['Team_Name'] == player_team2_selection].sort_values("Skater_Name")
        Puck_Positions = ('C', 'LW', 'RW', 'LD', 'RD', 'G')

        team1_goals = Team1_Game_Data['Goals'].iloc[0]
        team2_goals = Team2_Game_Data['Goals'].iloc[0]

        Game_Result = Team1_Game_Data['Game_Result'].iloc[0]
        st.markdown(f"<h3 style='text-align: center;'>Game Result</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<h5 style='text-align: center;'>{player_team1_code}({team1_goals}) - {player_team2_code}({team2_goals})</h5>",
            unsafe_allow_html=True
        )

        # Initialize row counts if needed
        if 'team1_rows' not in st.session_state:
            st.session_state.team1_rows = 5
        if 'team2_rows' not in st.session_state:
            st.session_state.team2_rows = 5

        def add_team1_row():
            st.session_state.team1_rows += 1

        def add_team2_row():
            st.session_state.team2_rows += 1

        # Combined form for both teams
        with st.form("Combined_Scoreboard_Form"):
            # Team 1 inputs
            st.header(f"{player_team1_selection} Players ({st.session_state.team1_rows})")
            team1_data = []
            for i in range(st.session_state.team1_rows):
                st.markdown("---")
                st.markdown(f"<h5 style='text-align: center;'>Player #{i + 1}</h5>", unsafe_allow_html=True)
                cols = st.columns(gap="medium", spec=[7, 5, 5])

                Team_1_Skater_Name = cols[0].selectbox(
                    "Name", Team_1_Roster["Skater_Name"],
                    key=f"Teams1_Player_Name_Select_{Week}_{Game_Number}_{i}"
                )
                Team_1_Skater_Type = cols[0].selectbox(
                    "Type", ("Skater", "Goalie"),
                    key=f"Teams1_Player_Type_Select_{Week}_{Game_Number}_{i}"
                )
                Team_1_Skater_Position = cols[0].selectbox(
                    "Pos", Puck_Positions,
                    key=f"Teams1_Player_Pos_Select_{Week}_{Game_Number}_{i}"
                )

                Team_1_Goals = cols[1].number_input(
                    "Goals", min_value=0, step=1,
                    key=f"team1_g_{Week}_{Game_Number}_{i}"
                )
                Team_1_Assists = cols[1].number_input(
                    "Assists", min_value=0, step=1,
                    key=f"team1_a_{Week}_{Game_Number}_{i}"
                )
                Team_1_Sog = cols[1].number_input(
                    "SOG", min_value=0, step=1,
                    key=f"team1_sog_{Week}_{Game_Number}_{i}"
                )

                Goalie_Goals_Allowed = cols[2].number_input(
                    "Goals Allowed - Goalie Only", min_value=0, step=1,
                    key=f"team1_goalie_goals_allowed_{Week}_{Game_Number}_{i}"
                )
                Goalie_Shots_Allowed = cols[2].number_input(
                    "Shots Allowed - Goalie Only", min_value=0, step=1,
                    key=f"team1_goalie_shots_allowed_{Week}_{Game_Number}_{i}"
                )
                Saves = cols[2].number_input(
                    "Saves - Goalie Only", min_value=0, step=1,
                    key=f"team1_saves_{Week}_{Game_Number}_{i}"
                )

                Plus_Minus = Team_1_Goals - Team1_Game_Data['Goals_Allowed'].iloc[0]
                Shoutout = Team1_Game_Data['Shoutout'].iloc[0]
                Team_Goals_Allowed = Team1_Game_Data['Goals_Allowed'].iloc[0]
                Team_Shots_Allowed = Team1_Game_Data['Shots_Allowed'].iloc[0]
                Team_GF = Team1_Game_Data['Goals'].iloc[0]

                team1_data.append({
                    "Team_Name": player_team1_selection,
                    "Team_Code": player_team1_code,
                    "Skater_Name": Team_1_Skater_Name,
                    "Skater_Type": Team_1_Skater_Type,
                    "Position": Team_1_Skater_Position,
                    "Week": Week,
                    "Game_Number": Game_Number,
                    "Goals": Team_1_Goals,
                    "Assists": Team_1_Assists,
                    "SOG": Team_1_Sog,
                    "Game_Result": Game_Result,
                    "Shoutout": Shoutout,
                    "Plus/Minus": Plus_Minus,
                    "Saves": Saves,
                    "Goalie_Goals Allowed": Goalie_Goals_Allowed,
                    "Goalie_Shots_Allowed": Goalie_Shots_Allowed,
                    "Team_Goals_Allowed": Team_Goals_Allowed,
                    "Team_Shots_Allowed": Team_Shots_Allowed,
                    "Team_GF": Team_GF,
                })

            # Team 2 inputs
            st.header(f"{player_team2_selection} Players ({st.session_state.team2_rows})")
            team2_data = []
            for i in range(st.session_state.team2_rows):
                st.markdown("---")
                st.markdown(f"<h5 style='text-align: center;'>Player #{i + 1}</h5>", unsafe_allow_html=True)
                cols = st.columns(gap="medium", spec=[7, 5, 5])

                Team_2_Skater_Name = cols[0].selectbox(
                    "Name", Team_2_Roster["Skater_Name"],
                    key=f"Teams2_Player_Name_Select_{Week}_{Game_Number}_{i}"
                )
                Team_2_Skater_Type = cols[0].selectbox(
                    "Type", ("Skater", "Goalie"),
                    key=f"Teams2_Player_Type_Select_{Week}_{Game_Number}_{i}"
                )
                Team_2_Skater_Position = cols[0].selectbox(
                    "Pos", Puck_Positions,
                    key=f"Teams2_Player_Pos_Select_{Week}_{Game_Number}_{i}"
                )

                Team_2_Goals = cols[1].number_input(
                    "Goals", min_value=0, step=1,
                    key=f"team2_g_{Week}_{Game_Number}_{i}"
                )
                Team_2_Assists = cols[1].number_input(
                    "Assists", min_value=0, step=1,
                    key=f"team2_a_{Week}_{Game_Number}_{i}"
                )
                Team_2_Sog = cols[1].number_input(
                    "SOG", min_value=0, step=1,
                    key=f"team2_sog_{Week}_{Game_Number}_{i}"
                )

                Goalie_Goals_Allowed = cols[2].number_input(
                    "Goals Allowed - Goalie Only", min_value=0, step=1,
                    key=f"team2_goalie_goals_allowed_{Week}_{Game_Number}_{i}"
                )
                Goalie_Shots_Allowed = cols[2].number_input(
                    "Shots Allowed - Goalie Only", min_value=0, step=1,
                    key=f"team2_goalie_shots_allowed_{Week}_{Game_Number}_{i}"
                )
                Saves = cols[2].number_input(
                    "Saves - Goalie Only", min_value=0, step=1,
                    key=f"team2_saves_{Week}_{Game_Number}_{i}"
                )

                Plus_Minus = Team_2_Goals - Team2_Game_Data['Goals_Allowed'].iloc[0]
                Shoutout = Team2_Game_Data['Shoutout'].iloc[0]
                Team_Goals_Allowed = Team2_Game_Data['Goals_Allowed'].iloc[0]
                Team_Shots_Allowed = Team2_Game_Data['Shots_Allowed'].iloc[0]
                Team_GF = Team2_Game_Data['Goals'].iloc[0]

                team2_data.append({
                    "Team_Name": player_team2_selection,
                    "Team_Code": player_team2_code,
                    "Skater_Name": Team_2_Skater_Name,
                    "Skater_Type": Team_2_Skater_Type,
                    "Position": Team_2_Skater_Position,
                    "Week": Week,
                    "Game_Number": Game_Number,
                    "Goals": Team_2_Goals,
                    "Assists": Team_2_Assists,
                    "SOG": Team_2_Sog,
                    "Game_Result": Game_Result,
                    "Shoutout": Shoutout,
                    "Plus/Minus": Plus_Minus,
                    "Saves": Saves,
                    "Goalie_Goals Allowed": Goalie_Goals_Allowed,
                    "Goalie_Shots_Allowed": Goalie_Shots_Allowed,
                    "Team_Goals_Allowed": Team_Goals_Allowed,
                    "Team_Shots_Allowed": Team_Shots_Allowed,
                    "Team_GF": Team_GF,
                })

            # Buttons to add rows for each team
            col_add_row = st.columns(2)
            with col_add_row[0]:
                add_row_team_1 = st.form_submit_button("Add Another Player to Team 1", on_click=add_team1_row)
            with col_add_row[1]:
                add_row_team_2 = st.form_submit_button("Add Another Player to Team 2", on_click=add_team2_row)

            # Submit button for all players
            submitted = st.form_submit_button("Submit Players")

        if submitted:
            new_data = pd.concat([pd.DataFrame(team1_data), pd.DataFrame(team2_data)], ignore_index=True)
            st.session_state.player_game_data = pd.concat([st.session_state.player_game_data, new_data], ignore_index=True)
            st.success("Player game data updated!")
            st.dataframe(st.session_state.player_game_data)

        if not st.session_state.player_game_data.empty:
            csv = st.session_state.player_game_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Raw_Player_Data as CSV",
                data=csv,
                file_name=f"Raw_Player_Data-{current_date}.csv",
                mime="text/csv"
            )
    else:
        st.warning("Please select both teams, week, and game number to continue.")


def home_page():
    st.markdown(f"<h1 style='text-align: center;'>PHL Data Entry Website</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>Season 3 - Version 1.0</h2>", unsafe_allow_html=True)

    # Upload 4 csv files and store in session_state
    PHL_Teams = load_or_init_csv("Upload PHL_Teams CSV", "PHL_Teams")
    PHL_Roster = load_or_init_csv("Upload PHL_Roster CSV", "PHL_Roster")
    st.markdown("---")  # horizontal separator
    team_game_data = load_or_init_csv("Upload Raw_Team_Data CSV", "team_game_data")
    player_game_data = load_or_init_csv("Upload Raw_Player_Data CSV", "player_game_data")

    st.markdown("---")  # horizontal separator

    # Optionally show the uploaded CSV preview
    if not PHL_Teams.empty:
        if st.checkbox("Show Team Preview", key="show_PHL_Teams_preview"):
            st.dataframe(PHL_Teams.style.hide(axis="index"))
    if not PHL_Roster.empty:
        if st.checkbox("Show Roster Preview", key="show_PHL_Roster_preview"):
            st.dataframe(PHL_Roster.style.hide(axis="index"))
    if not team_game_data.empty:
        if st.checkbox("Show Team Game Data Preview", key="show_team_data_preview"):
            st.dataframe(team_game_data.style.hide(axis="index"))
    if not player_game_data.empty:
        if st.checkbox("Show Player Game Data Preview", key="show_player_data_preview"):
            st.dataframe(player_game_data.style.hide(axis="index"))

def main():
    current_date = date.today()
    home_page()

    if all([
    'PHL_Teams' in st.session_state and not st.session_state['PHL_Teams'].empty,
    'PHL_Roster' in st.session_state and not st.session_state['PHL_Roster'].empty,
    'team_game_data' in st.session_state and not st.session_state['team_game_data'].empty,
    ]):
        Team_Data_Entry_Form(current_date)
        Player_Data_Entry_Form(current_date)
    else:
        st.warning("Please upload all 4 required CSV files to proceed.")

if __name__ == "__main__":
    main()
