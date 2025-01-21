# Requirements

## HiGHS binary
Download from https://github.com/JuliaBinaryWrappers/HiGHSstatic_jll.jl/releases

Run:
```bash copy
python3 generate_model.py
highs --options_file options.txt model.lp
```

## options.txt
Example:
```ini copy
write_solution_style=1
solution_file=solution.txt
mip_improving_solution_file=impr_solution.txt
```

## TEAM_PREFS_URL env var
Must return CSV formatted like this:
```csv copy
Капитан,Название команды,24 окт.,14 нояб.,28 нояб.,12 дек.,26 дек.,23 янв.,6 февр.,20 февр.,6 мар.,20 мар.,3 апр.,17 апр.
Иван Иванов,Лучшая команда,Совсем никак!,Совсем никак!,Совсем никак!,Готовы играть!,Совсем никак!,"Не очень удобно, но можем!",Готовы играть!,Готовы играть!,Готовы играть!,Готовы играть!,Готовы играть!,"Не очень удобно, но можем!"
```