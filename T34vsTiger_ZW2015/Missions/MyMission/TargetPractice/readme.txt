Mission Concept:

    Name: Target Practice

    Player: Starts in a Tiger I tank.

    Targets: 3 stationary or minimally active T-34/76 tanks marked as enemies.

    Objective: Destroy all 3 target tanks.

    Environment: Simple, clear day settings. Using map data copied from Mission_1 for simplicity.

Assumptions:

    You will create a mission folder structure like Missions\MyMissions\TargetPractice\.

    You will copy the necessary map data files (hmap.raw, hwater.raw, TerrainZone_c2m1.bmp, RouterZone_c2m1.bmp, micro_c2m1.bmp, lnd_c2m1.tex, forest_c2m1.tex) from Campaign_2\Mission_1\ into your new TargetPractice folder.

    You have Notepad++ (or a similar text editor) and GIMP (with DDS plugin) or Paint.NET for potential minor tweaks later.

    You will replace placeholder coordinates/matrices in content.script with actual locations determined using the editor.

    You will add this mission to MenuConfig.script.
	
	
	
	Instructions for Use:

    Create Folders: Make Missions\MyMissions\TargetPractice\.

    Copy Data Files: Copy hmap.raw, hwater.raw, TerrainZone_c2m1.bmp, RouterZone_c2m1.bmp, micro_c2m1.bmp, lnd_c2m1.tex, forest_c2m1.tex from Campaign_2\Mission_1\ into your TargetPractice folder.

    Save Scripts: Save each code block above into a text file with the corresponding filename (e.g., Mission.script, content.script) inside your TargetPractice folder.

    Add to Menu: Edit the main Scripts\MenuConfig.script file. Find the MissionLoadList array and add this line at the end (before the closing ];):

          
    ["Target Practice",       "CTargetPracticeMission"],

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.JavaScript
    IGNORE_WHEN_COPYING_END

    Use Editor for Placement:

        Load the TvT Level Editor.

        Go to File > Load level... and select "Target Practice".

        Use the editor's "Move" tool to select PlayerStartTank and place it where you want the player to begin.

        Select each target tank (TargetTank1, TargetTank2, TargetTank3) and place them where you want them. Use the "Rotate" tool to make them face the player area if desired.

        CRITICAL: After placing objects, go to File > Save level. This will overwrite your TargetPractice\content.script file with the new correct Matrix values for the objects you moved.

    Create Localization:

        Find your game's localization file (e.g., a .loc or .tsv file in a language folder).

        Add entries for the "TargetPractice" category with the keys "MissionName", "BriefingText", and "Objective01", providing the actual text you want displayed.

    TEST: Load the mission in the editor or game and see if it works! Check if targets appear, if they react (shoot back), and if the objective completes when you destroy all three.

This provides a solid, basic framework. You can expand on it by adding more targets, different target types, scenery, or more complex AI using MissionTasks.script. Remember to replace the placeholder matrices!