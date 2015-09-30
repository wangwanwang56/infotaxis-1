from __future__ import division

SCRIPT_ID = 'make_wind_tunnel_discretized_geom_configs'
SCRIPT_NOTES = 'Make all geom configs for all experiments and odor states.'

import imp

from db_api.connect import session
from db_api import models, add_script_execution

# get configuration
from config.make_wind_tunnel_discretized_geom_configs import *


def main(traj_limit=None):

    # add script execution to infotaxis database
    add_script_execution(script_id=SCRIPT_ID, notes=SCRIPT_NOTES, session=session)
    session.commit()

    # get wind tunnel connection and models
    wt_session = imp.load_source('db_api.connect', os.path.join(WT_REPO, 'db_api', 'connect.py')).session
    wt_models = imp.load_source('db_api.models', os.path.join(WT_REPO, 'db_api', 'models.py'))

    for experiment_id in EXPERIMENT_IDS:

        for odor_state in ODOR_STATES:

            # make geom_config_group
            geom_config_group_id = '{}_{}_odor_{}'.format(GEOM_CONFIG_GROUP_ID, experiment_id, odor_state)
            geom_config_group_desc = GEOM_CONFIG_GROUP_DESC.format(experiment_id, odor_state)
            geom_config_group = models.GeomConfigGroup(id=geom_config_group_id,
                                                       description=geom_config_group_desc)

            # get all wind tunnel trajectories of interest
            trajs = wt_session.query(wt_models.Trajectory).\
                filter(wt_models.Trajectory.experiment_id == experiment_id).\
                filter(wt_models.Trajectory.odor_state == odor_state).\
                filter(wt_models.Trajectory.clean is True)

            for tctr, traj in enumerate(trajs):

                positions = traj.positions(wt_session)

                discrete_trajectory = ENV.discretize_position_sequence(positions)
                discrete_duration = len(discrete_trajectory)
                avg_dt = .01 * len(positions) / discrete_duration
                geom_config = models.GeomConfig(duration=discrete_duration)
                geom_config.start_idx = discrete_trajectory[0]
                geom_config.geom_config_group = geom_config_group

                # add extension containing extra data about this geom_config
                ext = models.GeomConfigExtensionRealTrajectory(real_trajectory_id=traj.id,
                                                               avg_dt=avg_dt)
                geom_config.extension_real_trajectory = ext

                if traj_limit and (tctr == traj_limit - 1):
                    break

            session.add(geom_config_group)
            session.commit()

if __name__ == '__main__':
    main()