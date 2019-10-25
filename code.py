import argparse
import sys
import logging as log
from pathlib import Path

log.basicConfig(level=log.INFO)

years = list(range(1880, 2019))

def summary(benchmark_dir: Path, result_dir: Path, out, years):
    header = ['Year', 'Male Err Type 1 Wt', 'Male Err Type 1 Unwt', 'Male Err Type 2 Wt', 'Male Err Type 2 Unwt', 
              'Male Err Type 3 Wt', 'Male Err Type 3 Unwt', 'Female Err Type 1 Wt', 'Female Err Type 1 Unwt',
              'Female Err Type 2 Wt', 'Female Err Type 2 Unwt', 'Female Err Type 3 Wt', 'Female Err Type 3 Unwt']          
    delim = '\t'
    out.write(delim.join(header) + '\n')
    res = []
    for year in years:
        male = benchmark_dir / f'male{year}.txt_withsent_isaperson'
        female = benchmark_dir / f'female{year}.txt_withsent_isaperson'
        assert male.exists()
        assert female.exists()
        males = [line.split(',') for line in male.read_text().splitlines()]
        females = [line.split(',') for line in female.read_text().splitlines()]

        # name and freq
        males = [(x[0].split()[0], int(x[2])) for x in males]
        females = [(x[0].split()[0], int(x[2])) for x in females]

        male_res_file = result_dir / f'male{year}.txt'
        female_res_file = result_dir / f'female{year}.txt'
        assert male_res_file.exists()
        assert female_res_file.exists()
        male_res = male_res_file.read_text().splitlines()
        female_res = female_res_file.read_text().splitlines()

        assert len(males) == len(male_res)
        assert len(females) == len(female_res)

        year_row = [-1.0] * 12  # 12 cols

        # Error Type 1 Weighted
        male_error = sum(freq for (name, freq), x in zip(males, male_res) if (x[0:3]!='PER'))
        female_error = sum(freq for (name, freq), x in zip(females, female_res) if (x[0:3]!='PER'))
        year_row[0] = male_error / sum(f for _, f in males)
        year_row[6 + 0] = female_error / sum(f for _, f in females)

        # Error Type 1 Unweighted 
        year_row[1] = sum(1 for x in male_res if (x[0:3]!='PER')) / len(male_res)
        year_row[6 + 1] = sum(1 for x in female_res if (x[0:3]!='PER')) / len(female_res)

        # Error Type 2 Weighted 
        male_error = [(x, freq) for (name, freq), x in zip(males, male_res) if (x[0:3]!='PER' and x!="")]
        female_error = [(x, freq) for (name, freq), x in zip(females, female_res) if (x[0:3]!='PER' and x!="")]
        year_row[2] =  sum(f for x, f in male_error)/ sum(f for _, f in males)
        year_row[6 + 2] =  sum(f for x, f in female_error)/ sum(f for _, f in females)

        # Error Type 2 Unweighted
        year_row[3] = sum(1 for x in male_res if (x[0:3]!='PER' and x!="")) / len(male_res)
        year_row[6 + 3] = sum(1 for x in female_res if (x[0:3]!='PER' and x!="")) / len(female_res)

        # Error Type 3 Weighted
        male_error = [(x, freq) for (name, freq), x in zip(males, male_res) if (x=="")]
        female_error = [(x, freq) for (name, freq), x in zip(females, female_res) if (x=="")]
        year_row[4] =  sum(f for x, f in male_error)/ sum(f for _, f in males)
        year_row[6 + 4] =  sum(f for x, f in female_error)/ sum(f for _, f in females)

        # Error Type 3 Unweighted
        year_row[5] = sum(1 for x in male_res if (x=="")) / len(male_res)
        year_row[6 + 5] = sum(1 for x in female_res if (x=="")) / len(female_res)

        out.write(delim.join(f'{x:g}' for x in [year] + year_row) + '\n')

def process(file_path, model_path, output):
    file_dir = Path(file_path)
    model_dir = Path(model_path)
    with open(output + '.tsv', 'w') as out:
        summary(file_dir, model_dir, out=out, years=years)

if __name__ == '__main__':
    process("./benchmark/Template_4",sys.argv[1],sys.argv[2])
    
