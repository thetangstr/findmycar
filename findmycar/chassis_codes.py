#!/usr/bin/env python3
"""
Chassis code knowledge base for proper vehicle identification
"""

# Common chassis codes mapped to make, model, and year ranges
CHASSIS_CODES = {
    # Honda Civic chassis codes
    'EG6': {'make': 'Honda', 'model': 'Civic', 'year_min': 1992, 'year_max': 1995, 'variant': 'SiR/VTi Hatchback'},
    'EG8': {'make': 'Honda', 'model': 'Civic', 'year_min': 1992, 'year_max': 1995, 'variant': 'Sedan'},
    'EG9': {'make': 'Honda', 'model': 'Civic', 'year_min': 1992, 'year_max': 1995, 'variant': 'Ferio'},
    'EK4': {'make': 'Honda', 'model': 'Civic', 'year_min': 1996, 'year_max': 2000, 'variant': 'SiR'},
    'EK9': {'make': 'Honda', 'model': 'Civic', 'year_min': 1997, 'year_max': 2000, 'variant': 'Type R'},
    'EM1': {'make': 'Honda', 'model': 'Civic', 'year_min': 1999, 'year_max': 2000, 'variant': 'Si Coupe'},
    'EP3': {'make': 'Honda', 'model': 'Civic', 'year_min': 2001, 'year_max': 2005, 'variant': 'Type R/Si'},
    'FD2': {'make': 'Honda', 'model': 'Civic', 'year_min': 2006, 'year_max': 2011, 'variant': 'Type R'},
    'FK8': {'make': 'Honda', 'model': 'Civic', 'year_min': 2017, 'year_max': 2021, 'variant': 'Type R'},
    'FL5': {'make': 'Honda', 'model': 'Civic', 'year_min': 2022, 'year_max': 2024, 'variant': 'Type R'},
    
    # Honda Accord chassis codes
    'CB7': {'make': 'Honda', 'model': 'Accord', 'year_min': 1990, 'year_max': 1993, 'variant': '4th Gen'},
    'CD5': {'make': 'Honda', 'model': 'Accord', 'year_min': 1994, 'year_max': 1997, 'variant': '5th Gen'},
    'CG': {'make': 'Honda', 'model': 'Accord', 'year_min': 1998, 'year_max': 2002, 'variant': '6th Gen'},
    'CL7': {'make': 'Honda', 'model': 'Accord', 'year_min': 2003, 'year_max': 2007, 'variant': 'Euro R'},
    'CL9': {'make': 'Honda', 'model': 'Accord', 'year_min': 2003, 'year_max': 2007, 'variant': '7th Gen'},
    
    # Honda S2000 chassis code
    'AP1': {'make': 'Honda', 'model': 'S2000', 'year_min': 1999, 'year_max': 2003, 'variant': '2.0L'},
    'AP2': {'make': 'Honda', 'model': 'S2000', 'year_min': 2004, 'year_max': 2009, 'variant': '2.2L'},
    
    # Honda Integra/RSX chassis codes
    'DC2': {'make': 'Honda', 'model': 'Integra', 'year_min': 1994, 'year_max': 2001, 'variant': 'Type R'},
    'DC5': {'make': 'Honda', 'model': 'RSX', 'year_min': 2002, 'year_max': 2006, 'variant': 'Type S'},
    
    # Toyota chassis codes
    'AE86': {'make': 'Toyota', 'model': 'Corolla', 'year_min': 1983, 'year_max': 1987, 'variant': 'GT-S/Trueno'},
    'JZA80': {'make': 'Toyota', 'model': 'Supra', 'year_min': 1993, 'year_max': 2002, 'variant': 'Mk4'},
    'JZA70': {'make': 'Toyota', 'model': 'Supra', 'year_min': 1986, 'year_max': 1992, 'variant': 'Mk3'},
    'SW20': {'make': 'Toyota', 'model': 'MR2', 'year_min': 1990, 'year_max': 1999, 'variant': '2nd Gen'},
    'ZZW30': {'make': 'Toyota', 'model': 'MR2', 'year_min': 2000, 'year_max': 2007, 'variant': 'Spyder'},
    'GR86': {'make': 'Toyota', 'model': '86', 'year_min': 2022, 'year_max': 2024, 'variant': 'GR'},
    'ZN6': {'make': 'Toyota', 'model': '86', 'year_min': 2013, 'year_max': 2021, 'variant': 'GT86/FRS'},
    
    # Nissan chassis codes
    'S13': {'make': 'Nissan', 'model': '240SX', 'year_min': 1989, 'year_max': 1994, 'variant': 'Silvia'},
    'S14': {'make': 'Nissan', 'model': '240SX', 'year_min': 1995, 'year_max': 1998, 'variant': 'Silvia'},
    'S15': {'make': 'Nissan', 'model': 'Silvia', 'year_min': 1999, 'year_max': 2002, 'variant': 'Spec R'},
    'R32': {'make': 'Nissan', 'model': 'Skyline', 'year_min': 1989, 'year_max': 1994, 'variant': 'GT-R'},
    'R33': {'make': 'Nissan', 'model': 'Skyline', 'year_min': 1995, 'year_max': 1998, 'variant': 'GT-R'},
    'R34': {'make': 'Nissan', 'model': 'Skyline', 'year_min': 1999, 'year_max': 2002, 'variant': 'GT-R'},
    'R35': {'make': 'Nissan', 'model': 'GT-R', 'year_min': 2007, 'year_max': 2024, 'variant': 'GT-R'},
    'Z32': {'make': 'Nissan', 'model': '300ZX', 'year_min': 1990, 'year_max': 1996, 'variant': 'Twin Turbo'},
    'Z33': {'make': 'Nissan', 'model': '350Z', 'year_min': 2003, 'year_max': 2009, 'variant': '350Z'},
    'Z34': {'make': 'Nissan', 'model': '370Z', 'year_min': 2009, 'year_max': 2020, 'variant': '370Z'},
    
    # Mazda chassis codes
    'NA': {'make': 'Mazda', 'model': 'Miata', 'year_min': 1990, 'year_max': 1997, 'variant': 'MX-5'},
    'NB': {'make': 'Mazda', 'model': 'Miata', 'year_min': 1998, 'year_max': 2005, 'variant': 'MX-5'},
    'NC': {'make': 'Mazda', 'model': 'Miata', 'year_min': 2006, 'year_max': 2015, 'variant': 'MX-5'},
    'ND': {'make': 'Mazda', 'model': 'Miata', 'year_min': 2016, 'year_max': 2024, 'variant': 'MX-5'},
    'FD': {'make': 'Mazda', 'model': 'RX-7', 'year_min': 1992, 'year_max': 2002, 'variant': 'FD3S'},
    'FC': {'make': 'Mazda', 'model': 'RX-7', 'year_min': 1986, 'year_max': 1991, 'variant': 'FC3S'},
    
    # Subaru chassis codes
    'GC8': {'make': 'Subaru', 'model': 'Impreza', 'year_min': 1992, 'year_max': 2000, 'variant': 'WRX/STI'},
    'GD': {'make': 'Subaru', 'model': 'Impreza', 'year_min': 2001, 'year_max': 2007, 'variant': 'WRX/STI'},
    'GR': {'make': 'Subaru', 'model': 'Impreza', 'year_min': 2008, 'year_max': 2014, 'variant': 'WRX/STI'},
    'VA': {'make': 'Subaru', 'model': 'WRX', 'year_min': 2015, 'year_max': 2021, 'variant': 'STI'},
    'VB': {'make': 'Subaru', 'model': 'WRX', 'year_min': 2022, 'year_max': 2024, 'variant': 'WRX'},
    'BRZ': {'make': 'Subaru', 'model': 'BRZ', 'year_min': 2013, 'year_max': 2024, 'variant': 'BRZ'},
    
    # Mitsubishi chassis codes
    'CP9A': {'make': 'Mitsubishi', 'model': 'Lancer', 'year_min': 1996, 'year_max': 2001, 'variant': 'Evolution IV-VI'},
    'CT9A': {'make': 'Mitsubishi', 'model': 'Lancer', 'year_min': 2001, 'year_max': 2007, 'variant': 'Evolution VII-IX'},
    'CZ4A': {'make': 'Mitsubishi', 'model': 'Lancer', 'year_min': 2008, 'year_max': 2016, 'variant': 'Evolution X'},
    
    # BMW chassis codes (E-codes)
    'E30': {'make': 'BMW', 'model': '3 Series', 'year_min': 1982, 'year_max': 1994, 'variant': 'E30'},
    'E36': {'make': 'BMW', 'model': '3 Series', 'year_min': 1990, 'year_max': 2000, 'variant': 'E36'},
    'E46': {'make': 'BMW', 'model': '3 Series', 'year_min': 1997, 'year_max': 2006, 'variant': 'E46'},
    'E90': {'make': 'BMW', 'model': '3 Series', 'year_min': 2005, 'year_max': 2013, 'variant': 'E90/E92/E93'},
    'F80': {'make': 'BMW', 'model': 'M3', 'year_min': 2014, 'year_max': 2020, 'variant': 'F80'},
    'G80': {'make': 'BMW', 'model': 'M3', 'year_min': 2021, 'year_max': 2024, 'variant': 'G80'},
}

def parse_chassis_code(query: str) -> dict:
    """
    Parse chassis codes from search query
    Returns vehicle information if chassis code is found
    """
    query_upper = query.upper()
    
    # Look for chassis codes in the query
    for code, info in CHASSIS_CODES.items():
        if code in query_upper:
            return {
                'make': info['make'],
                'model': info['model'],
                'year_min': info['year_min'],
                'year_max': info['year_max'],
                'chassis_code': code,
                'variant': info.get('variant', ''),
                'found': True
            }
    
    return {'found': False}