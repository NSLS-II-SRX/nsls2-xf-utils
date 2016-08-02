from skxray.fluorescence import XrfElement as Element
e = Element('Cu')

#provide binding energy
e.bind_energy.all

#provide emission line
e.emission_line.all
e.emission_line['ka1']

#provideenergy, calculate cross section
e.cs(12).all
