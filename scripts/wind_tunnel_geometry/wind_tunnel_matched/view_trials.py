"""View trials generated by the wind_tunnel_matched infotaxis simulation."""

SIMULATIONID = 'wind_tunnel_matched_fruitfly_0.4mps_odor_off'

import matplotlib.pyplot as plt
plt.ion()

from plume import CollimatedPlume
from trial import Trial
from plotting import plume_and_traj_3d as plot_trial

from db_api import models
from db_api.connect import session


# get simulation
sim = session.query(models.Simulation).get(SIMULATIONID)

pl = CollimatedPlume(sim.env, sim.dt, orm=sim.plume)

_, axs = plt.subplots(2, 1, facecolor='w', figsize=(10, 10))
plt.draw()

for tr_orm in sim.trials:
    [ax.cla() for ax in axs]

    pl.set_src_pos(tr_orm.geom_config.src_idx, is_idx=True)
    pl.initialize()

    trial = Trial(pl, None, orm=tr_orm)
    trial.bind_timepoints(models, session)

    plot_trial(axs, trial)
    axs[0].set_title('trial {} from {}'.format(trial.orm.id, sim.id))
    plt.draw()

    raw_input('Press enter to continue...')