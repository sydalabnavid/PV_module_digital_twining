from pvlib import pvsystem
import pandas as pd
import matplotlib.pyplot as plt

# module parameters for the Offgridtec Mono 20W 3-01-001560:
parameters = {
    'Name': 'Offgridtec_001560',
    'BIPV': 'ESG_glass',
    'Date': '04/05/2023',
    'celltype': 'monocrystalline', # technology
    'Bifacial':True, #True/False                                                    
    'T_NOCT': 45,
    # 'STC': 224.99, # Standard Test Conditions power
    # 'PTC': 203.3, # PVUSA Test Condition power
    # 'A_c': 1.7, #module cells area in m² 
    'N_s': 36, #number of cells in series
    'Pmax': 20,
    'I_sc_ref': 1.21, #Short circuit current (ISC)
    'V_oc_ref': 22.3, #Open circuit voltage (VOC)
    'I_mp_ref': 1.12, #max. current (IMP)
    'V_mp_ref': 17.8,
    'MSV':600, #Maximum system voltage
    'alpha_sc': 0.0045, #short circuit current temperature coefficient in A/Δ°C          *************
    # 'beta_oc': -0.22216, #open circuit voltage temperature coefficient in V/Δ°C
    'a_ref': 1.3825, #diode ideality factor                                                *************        
    'I_L_ref': 1.21, #light or photogenerated current at reference condition in A         *************
    'I_o_ref': 883e-10, #diode saturation current at reference condition in A            *************
    'R_s': 0.9987, # series resistance in Ω                                                 *************
    'R_sh_ref': 3941.111, #shunt resistance at reference condition in Ω                      *************
    # 'Adjust': 8.7, #adjustment to short circuit temperature coefficient in %
    # 'gamma_r': -0.476, #power temperature coefficient at reference condition in %/Δ°
}


cases = [
    # (1000, 25),
    # (800, 25),
    # (600, 25),
    # (400, 25),
    # (200, 25),
    (805.88, 18),
    (930.07, 29.1),
    (663.63, 26.3),
    (554.17, 13.2)
]

conditions = pd.DataFrame(cases, columns=['Geff', 'Tcell'])

# adjust the reference parameters according to the operating
# conditions using the De Soto model:
IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
    conditions['Geff'],
    conditions['Tcell'],
    alpha_sc=parameters['alpha_sc'],
    a_ref=parameters['a_ref'],
    I_L_ref=parameters['I_L_ref'],
    I_o_ref=parameters['I_o_ref'],
    R_sh_ref=parameters['R_sh_ref'],
    R_s=parameters['R_s'],
    EgRef=1.121,
    dEgdT=-0.0002677
)

# plug the parameters into the SDE and solve for IV curves:
curve_info = pvsystem.singlediode(
    photocurrent=IL,
    saturation_current=I0,
    resistance_series=Rs,
    resistance_shunt=Rsh,
    nNsVth=nNsVth,
    ivcurve_pnts=100,
    method='lambertw'
)

# plot the calculated curves:
plt.figure()
for i, case in conditions.iterrows():
    label = (
        "$G_{eff}$ " + f"{case['Geff']} $W/m^2$\n"
        "$T_{cell}$ " + f"{case['Tcell']} $\\degree C$"
    )
    plt.plot(curve_info['v'][i], curve_info['i'][i], label=label)
    v_mp = curve_info['v_mp'][i]
    i_mp = curve_info['i_mp'][i]
    # mark the MPP
    plt.plot([v_mp], [i_mp], ls='', marker='o', c='k')

plt.legend(loc=(1.0, 0))
plt.xlabel('Module voltage [V]')
plt.ylabel('Module current [A]')
plt.title(parameters['Name'])
plt.show()
plt.gcf().set_tight_layout(True)


# draw trend arrows
def draw_arrow(ax, label, x0, y0, rotation, size, direction):
    style = direction + 'arrow'
    bbox_props = dict(boxstyle=style, fc=(0.8, 0.9, 0.9), ec="b", lw=1)
    t = ax.text(x0, y0, label, ha="left", va="bottom", rotation=rotation,
                size=size, bbox=bbox_props, zorder=-1)

    bb = t.get_bbox_patch()
    bb.set_boxstyle(style, pad=0.6)


ax = plt.gca()
draw_arrow(ax, 'Irradiance', 20, 2.5, 90, 15, 'r')
draw_arrow(ax, 'Temperature', 35, 1, 0, 15, 'l')

print(pd.DataFrame({
    'i_sc': curve_info['i_sc'],
    'v_oc': curve_info['v_oc'],
    'i_mp': curve_info['i_mp'],
    'v_mp': curve_info['v_mp'],
    'p_mp': curve_info['p_mp'],
}))
