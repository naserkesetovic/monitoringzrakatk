import os
import mztk

from PyInquirer import prompt, Separator

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

main_screen = [
    {
        'type': 'list',
        'message': 'Odaberite?',
        'name': 'main',
        'choices': [
            Separator(),
            'Unesi grad',
            'Prikaži sve gradove',
            Separator(),
            'Odustani'
        ]
    }
]

def formatiraj_grad(unos):
    return unos.lower().strip().replace('č','c').replace('ć', 'c').replace('ž', 'z').replace(' ', '-')

def unesi_grad():
    grad = formatiraj_grad(Prompt.ask('Ime grada:', default = 'Lukavac'))

    with console.status('Prikupljam podatke...', spinner='dots'):
        try:
            podaci = mztk.mztk(grad)
        except Exception as e:
            print(e)
            return 

    os.system('cls||clear')
    console.rule("http://monitoringzrakatk.info")
    console.print()
    table = Table(show_header = True, header_style = 'bold magenta', box = box.SIMPLE_HEAVY, title="[bold]{0}[/bold]".format(podaci.grad.capitalize()), expand = True, show_footer = True)
    table.add_column('Podatak')
    table.add_column('Vrijednost', justify = 'right')
    table.add_column('Podatak')
    table.add_column('Vrijednost', justify = 'right')

    table.add_row("SO2:", str(podaci.so2) + ' µg/m³', "Relativna vlažnost", str(podaci.h) + '    %' )
    table.add_row("NO2:", str(podaci.no2) + ' µg/m³', "Zračni pritisak", str(podaci.p) + ' mBar' )
    table.add_row("CO:", str(podaci.co) + ' mg/m³', "Temperatura", str(podaci.t) + '   °C' )
    table.add_row("O3:", str(podaci.o3) + ' µg/m³', "Brzina vjetra", str(podaci.ws) + '  m/s' )
    table.add_row("PM25:", str(podaci.pm25) + ' µg/m³', "Smjer vjetra", str(podaci.wd) + '    °' )

    console.print(table, justify = 'center')
    console.print("Podaci su od {0} ({1}).".format(podaci.posljednja_provjera_mztk().lower(), podaci.mztk_vrijeme))
    console.rule()

def prikazi_gradove():
    os.system('cls||clear')
    console.rule('Gradovi:')
    i = 0
    for g in mztk.gradovi:
        i += 1
        print("{0}. {1}".format(i, g.capitalize()))

    unesi_grad()

def main():
    os.system('cls||clear')
    console.rule('[bold]Menu[/bold]')

    anws = prompt(main_screen)

    if anws.get('main') == 'Unesi grad':
        unesi_grad()

    elif anws.get('main') == 'Prikaži sve gradove':
        prikazi_gradove()

    else:
        exit()

if __name__ == '__main__':
    main()