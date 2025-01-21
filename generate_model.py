# import highspy
import csv
import os
import requests

TEAMS_COUNT = 9
DUELS_PER_DAY = 3
DUELS_COUNT = TEAMS_COUNT * (TEAMS_COUNT - 1) // 2
DAYS_COUNT = DUELS_COUNT // DUELS_PER_DAY
TEAM_PREFS_URL = os.environ.get('TEAM_PREFS_URL')

print('Generating MPS model for %d teams, %d duels in %d days' % (TEAMS_COUNT, DUELS_COUNT, DAYS_COUNT))

with open('model.lp', 'w') as model:
    # Let 𝑥𝑑,𝑡 be a zero-or-one variable, that is 1 iff team 𝑡 plays on day 𝑑.
    all_x_vars = []
    for d in range(DAYS_COUNT):
        for t in range(TEAMS_COUNT):
            all_x_vars.append('x_d%d_t%d' % (d, t))

    # Let 𝑦𝑑,𝑡,𝑢 be a zero-or-one variable, that is 1 iff team 𝑡 plays team 𝑢 in one of the duels on day 𝑑
    #  (we treat 𝑦𝑑,𝑡,𝑢 as identical to 𝑦𝑑,𝑢,𝑡).
    all_y_vars = []
    for d in range(DAYS_COUNT):
        for t in range(TEAMS_COUNT):
            for u in range(t+1, TEAMS_COUNT):
                all_y_vars.append('y_d%d_t%d_u%d' % (d, t, u))

    # Finally, minimize ∑𝑑,𝑡𝑥𝑑,𝑡, which counts the sum of the number of teams to the venue each day.
    model.write('Minimize\n  ' + ' + '.join(all_x_vars) + '\n')

    model.write('Subject To\n')
    # Three duels per day: ∑𝑡,𝑢𝑦𝑑,𝑡,𝑢=3 for each 𝑑 (where the sum is over 𝑡,𝑢 such that 𝑡<𝑢).
    for d in range(DAYS_COUNT):
        model.write('  ')
        for t in range(TEAMS_COUNT):
            for u in range(t+1, TEAMS_COUNT):
                model.write('y_d%d_t%d_u%d' % (d, t, u))
                if t < TEAMS_COUNT - 2:
                    model.write(' + ')
        model.write(' = %d\n' % DUELS_PER_DAY)
    
    # 𝑥/𝑦 consistency: 𝑥𝑑,𝑡≤∑𝑢𝑦𝑑,𝑡,𝑢 and 𝑥𝑑,𝑡≥𝑦𝑑,𝑡,𝑢 for each 𝑢.
    for d in range(DAYS_COUNT):
        for t in range(TEAMS_COUNT):
            ys = []
            for u in range(t):
                model.write('  x_d%d_t%d - y_d%d_t%d_u%d >= 0\n' % (d, t, d, u, t))
                ys.append('y_d%d_t%d_u%d' % (d, u, t))
            for u in range(t+1, TEAMS_COUNT):
                model.write('  x_d%d_t%d - y_d%d_t%d_u%d >= 0\n' % (d, t, d, t, u))
                ys.append('y_d%d_t%d_u%d' % (d, t, u))
            model.write('  ' + ' + '.join(ys) + ' - x_d%d_t%d >= 0\n' % (d, t))
    
    # Round robin format: ∑𝑑𝑦𝑑,𝑡,𝑢=1 for each 𝑡,𝑢 such that 𝑡<𝑢.
    for t in range(TEAMS_COUNT):
        for u in range(t+1, TEAMS_COUNT):
            model.write('  ')
            for d in range(DAYS_COUNT):
                model.write('y_d%d_t%d_u%d' % (d, t, u))
                if d < DAYS_COUNT - 1:
                    model.write(' + ')
            model.write(' = 1\n')

    # No team should play all three games in a day
    for d in range(DAYS_COUNT):
        for t in range(TEAMS_COUNT):
            ys = []
            for u in range(t):
                ys.append('y_d%d_t%d_u%d' % (d, u, t))
            for u in range(t+1, TEAMS_COUNT):
                ys.append('y_d%d_t%d_u%d' % (d, t, u))
            model.write('  ' + ' + '.join(ys) + ' <= 2\n')

    # Consider team preferences
    response = requests.get(TEAM_PREFS_URL)
    response.raise_for_status()
    csv_reader = csv.reader(response.text.splitlines())
    for t1, row in enumerate(csv_reader):
        if t1 == 0:
            continue
        for d in range(DAYS_COUNT):
            if row[d+2].startswith('Совсем никак'): # or row[d+2].startswith('Не очень'):
                model.write('  x_d%d_t%d <= 0\n' % (d, t1-1))

    # 0≤𝑥𝑑,𝑡≤1 and 0≤𝑦𝑑,𝑡,𝑢≤1.
    model.write('Binary\n  ' + ' '.join(all_x_vars) + ' ' + ' '.join(all_y_vars) + '\n')

    model.write('End\n')

# h = highspy.Highs()
# filename = '/Users/alexkir/Downloads/model.lp'
# h.readModel(filename)
# h.run()
# print('Model ', filename, ' has status ', h.getModelStatus())

# solution = h.getSolution()
# for index, name in enumerate(all_x_vars):
#     print(f'{name} = {solution.col_value[index]:2.0f}')
# for index, name in enumerate(all_y_vars):
#     if solution.col_value[index + len(all_x_vars)] > 0.1:
#         print(f'{name} = {solution.col_value[index + len(all_x_vars)]:2.0f}')
