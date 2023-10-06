import xarray as xr
import numpy as np
from glob import glob
import os
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument ('--variable', type = str, default='pr',
                     help = 'Choose the variable')

parser.add_argument('--exp', type=str, default='dcppA-hindcast',
                    help='Experiment of CMIP6')

args = parser.parse_args()
experiment = args.exp
var = args.variable


def contruct_filename(filename):

    variavel = filename[0].split("/")[-1].split('_')[0]
    frequency = filename[0].split("/")[-1].split('_')[1]
    modelo = filename[0].split("/")[-1].split('_')[2] 
    cenario = filename[0].split("/")[-1].split('_')[3]
    subexp = filename[0].split("/")[-1].split('_')[4][0:5]
    member = filename[0].split("/")[-1].split('_')[4].split("-")[1]
    grid_label = filename[0].split("/")[-1].split('_')[5]

    date_start = filename[0].split("/")[-1].split('_')[-2].split('-')[0]
    date_end = filename[-1].split("/")[-1].split('_')[-2].split('-')[-1]

    #pr_Amon_EC-Earth3_dcppA-hindcast_s1973-r1i1p1f1_gr_197311-197410_ce.nc
    name_arq = f'{variavel}_{frequency}_{modelo}_{cenario}_{subexp}-{member}_{grid_label}_{date_start}-{date_end}_ce.nc'
    
    return name_arq


if __name__ == '__main__': 

    cdir = "./"
    wdir = cdir + f'{experiment}/'

    models = [d for d in os.listdir(wdir) if os.path.isdir(os.path.join(wdir,d))]

    if experiment == 'dcppA-hindcast':
            subexp_year_start = 1973
            subexp_year_end = 2018
    if experiment == 'dcppB-forecast':
            subexp_year_start = 2019
            subexp_year_end = 2021

    for model in sorted(models):
        fin = f'{wdir}{model}/Amon/{var}/'
        
        file_list_test = sorted(glob(f'{fin}s{subexp_year_start}/ce/{var}_Amon_{model}_{experiment}_s{subexp_year_start}-r*i1*.nc'))
        members = [i.split("/")[-1].split("_")[4].split("-")[1] for i in file_list_test]
        member = len(np.unique(members))

        if len(file_list_test) == member:
            print("** Modelo não está subdividido**")
            print()
        
        else:
            print(f"** {model} está subdividido")

            for subexp in range(subexp_year_start,subexp_year_end+1):               
                for member in range(1,member+1):
                    
                    print('Iniciando junção:', model, f's{subexp}', member)
  
                    # Create a list of netCDF file names to concatenate
                    file_list = sorted(glob(f'{fin}s{subexp}/ce/{var}_Amon_{model}_{experiment}_s{subexp}-r{member}i1p*.nc'))
                    
                    if file_list:
                        # Open each netCDF file and concatenate along the time dimension
                        ds_list = [xr.open_dataset(file, decode_times=False) for file in file_list]
                        ds_concat = xr.concat(ds_list, dim='time')
                        
                        ds_concat.time_bnds.attrs['units'] = ds_concat.time.attrs['units']
                        ds_concat.time_bnds.attrs['calendar'] = ds_concat.time.attrs['calendar']

                        ds_concat = xr.decode_cf(ds_concat)

                        #Create nome to file
                        filename = contruct_filename(file_list)

                        print('Salvando arquivo concatenado')
                        ds_concat.to_netcdf(f'{fin}s{subexp}/{filename}')
                        print('Finish')
                    else:
                        pass

                print("=================================================================================================================")
                print('')


                


