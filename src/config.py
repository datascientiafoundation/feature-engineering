from collections import defaultdict

sensors_config = {
    'application': defaultdict(list,
                                    # keep the following categories: app_communication, app_education, app_maps_&_navigation,
                                    # app_social, app_travel_&_local, app_productivity
                                    columns_to_exclude=['app_not-found', 'app_news_&_magazines',
                                                        'app_business', 'app_tools', 'app_personalization',
                                                        'app_strategy', 'app_food_&_drink',
                                                        'app_health_&_fitness', 'app_auto_&_vehicles', 'app_shopping',
                                                        'app_weather', 'app_lifestyle',
                                                        'app_action', 'app_art_&_design', 'app_entertainment',
                                                        'app_trivia', 'app_board',
                                                        'app_word', 'app_photography', 'app_finance',
                                                        'app_books_&_reference',
                                                        'app_video_players_&_editors', 'app_puzzle',
                                                        'app_libraries_&_demo',
                                                        'app_sports', 'app_racing', 'app_music_&_audio', 'app_casino',
                                                        'app_role_playing', 'app_simulation', 'app_adventure',
                                                        'app_educational', 'app_dating', 'app_music', 'app_card',
                                                        'app_casual',
                                                        'app_medical', 'app_beauty', 'app_arcade', 'app_parenting',
                                                        'app_comics', 'app_house_&_home'],
                                    normalization=['app_nunique', 'app_category_nunique']),
    'wifi': defaultdict(list),
    'wifinetworks': defaultdict(list),
    'locationpertime': defaultdict(list),
    'cellularnetwork': defaultdict(list),
    'stepdetector': defaultdict(list),
    'stepcounter': defaultdict(list),
    'touch': defaultdict(list),
    'notification': defaultdict(list,
                                     normalization=['notification_posted', 'notification_removed']),
    'bluetoothnormal': defaultdict(list),
    'bluetoothlowenergy': defaultdict(list),
    # 'gyroscope': defaultdict(list),
    # 'magneticfield': defaultdict(list),
    'batterycharge': defaultdict(list,
                                      min_max_normalization=['battery_charging_ac', 'battery_charging_unknown',
                                                             'battery_charging_usb', 'battery_charging_wifi',
                                                             'battery_no_charging']),
    'proximity': defaultdict(list,
                                  columns_to_exclude=[]
                                  ),
    'screen':
        defaultdict(list,
                    columns_to_exclude=[],
                    min_max_normalization=['screen_mean_seconds_per_episode', 'screen_min_seconds_per_episode',
                                           'screen_max_seconds_per_episode', 'screen_std_seconds_per_episode',
                                           'screen_SCREEN_ON', 'screen_SCREEN_OFF'],
                    ),
    'activitiespertime': defaultdict(list,
                                     min_max_normalization=['activity_Still', 'activity_Tilting', 'activity_Unknown',
                                                            'activity_OnFoot', 'activity_OnBycicle',
                                                            'activity_InVehicle']
                                     ),
    'userpresence': defaultdict(list,
                                     min_max_normalization=['user_presence_False', 'user_presence_True']
                                     ),
    'airplanemode': defaultdict(list,
                                     min_max_normalization=['airplanemode_False', 'airplanemode_True']
                                     ),
    'headsetplug': defaultdict(list,
                                    min_max_normalization=['headset_True', 'headset_False']
                                    ),
    'ringmode': defaultdict(list,
                                 min_max_normalization=['ringmode_mode_normal', 'ringmode_mode_vibrate',
                                                        'ringmode_mode_silent']),
    'music': defaultdict(list,
                              min_max_normalization=['music_False', 'music_True']
                              ),
    'batterymonitoringlog':
        defaultdict(list,
                    columns_to_exclude=['battery_timestamp_first', 'battery_timestamp_last', 'battery_level_first',
                                        'battery_level_last']
                    )
}
