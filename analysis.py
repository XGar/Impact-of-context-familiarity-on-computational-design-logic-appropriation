import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import lines
from matplotlib.gridspec import GridSpec

_context = ['Grasshopper', 'Hybrid', 'Rhino', 'Tot', 'Average']
niv = ['No experience', 'Novice', 'Limited', 'Basic', 'Advanced', 'Expert']
Software = ['Autocad', 'SketchUp', 'Rhino', 'Grasshopper', 'Revit',
            'Archicad', 'Average', 'Modeling', 'Bim', 'Rhino+GH']
feedback_col = ['Accessibility', 'Comprehension', 'Ease of Use', 'Usability', 'Satisfaction']
_color = sns.mpl_palette('Paired', 6)
_color2 = sns.mpl_palette('RdYlBu', 3)


# todo cleanup file, remove context analysis


def global_analysis(df, time_df, _study_columns, _title, _level='Context', o=None, sw='Average', detail=False):
    d = ['Level', 'Context', 'Order']
    b = Software.index(sw)
    study_columns = []
    study_columns.extend(_study_columns)
    if _level == 'Level':
        df1 = df.reset_index(_level, drop=False)
        df1[_level] = df1[_level].map(lambda _x: lvl(_x, b))
        df1.set_index([_level], append=True, inplace=True)
    else:
        df1 = df
    drop2 = ['Name']
    if o is not None:
        df1 = df1.xs(_context[o], level='Context')
        d.remove('Context')
    drop2.append(_level)
    df1 = df1.drop(0, level='Order')
    dd = []
    for item in df1.index.names:
        dd.append(item)
    dd.remove('Object')
    df2 = df1.groupby(level=dd, sort=False).sum()
    display(df2)
    a = df2.groupby(level=drop2, sort=False).sum()
    df1 = df1.droplevel([x for x in d if x != _level])
    time_ratio = (df1.droplevel('Object')['Time'] /
                  a.loc[df1.droplevel('Object').index]['Time'])
    time_ratio = pd.DataFrame(time_ratio.values, index=df1['Time'].index)
    a = df2.groupby(level=drop2, sort=False).mean()
    if 'Time' in a.columns:
        a['Time'] = a['Time'] / 60
    if 'Max' in a.columns:
        a['Max'] = a.loc[:, 'TileXSize':'DoorNumber'].max(axis=1)
    if 'CV' in a.columns:
        a['CV'] = a.loc[:, 'TileXSize':'DoorNumber'].std(axis=1) / a.loc[:, 'TileXSize':'DoorNumber'].mean(axis=1)
    if 'Rate' in study_columns:
        rate = _title + ' / Minute'
        a[rate] = a['Total'] / a['Time']
        study_columns[study_columns.index('Rate')] = _title + ' / Minute'

    a = a.sort_index(level=_level)
    c = detail
    if not c:
        length = a.index.get_level_values(_level).nunique()
    else:
        length = len(a.index.tolist())
    height = int(6 + length / 4)
    fig = plt.figure(figsize=(22, height), facecolor="#fefefe")
    title_suffix = _level
    if _level == 'Level':
        title_suffix = sw + ' level'
    if o is None:
        title = _title + ' by ' + title_suffix
    else:
        title = _context[o] + ": " + _title + ' by ' + title_suffix
    fig.suptitle(title, x=0.5, y=0.98, fontsize=20)
    grid_height = (5 + length / 4).__round__()
    gs = GridSpec(grid_height, 24, figure=fig, wspace=3, hspace=3 / grid_height)
    ax1 = fig.add_subplot(gs[1:4, :3])
    ax3 = fig.add_subplot(gs[1:4, 3:6])
    ax4 = fig.add_subplot(gs[1:4, 6:9])
    ax14 = fig.add_subplot(gs[1:4, 9:12])
    ax9 = fig.add_subplot(gs[4:, 12:])
    ax5 = fig.add_subplot(gs[4:, 12:])
    ax2 = fig.add_subplot(gs[2:4, 12:], sharex=ax9)
    ax6 = fig.add_subplot(gs[4:, :3])
    ax7 = fig.add_subplot(gs[4:, 3:6])
    ax8 = fig.add_subplot(gs[4:, 6:9])
    ax15 = fig.add_subplot(gs[4:, 9:12])
    ax10 = fig.add_subplot(gs[:1, :3])
    ax11 = fig.add_subplot(gs[:1, 3:6])
    ax12 = fig.add_subplot(gs[:1, 6:9])
    ax16 = fig.add_subplot(gs[:1, 9:12])
    ax13 = fig.add_subplot(gs[:2, 12:])

    _color3 = sns.mpl_palette("RdYlBu", 3)

    if _level == 'Context':
        def mapper(self):
            return _context.index(self)

        color_set = _color3
    elif _level == 'Order':
        def mapper(self):
            return self - 1

        color_set = _color3
    else:
        def mapper(self):
            return niv.index(self)

        _color3 = _color
        a = a.reset_index(_level, drop=False)
        color_set = a.groupby([_level], as_index=False).mean()[_level].map(lambda _x: _color[_x])
        a[_level] = a[_level].map(lambda _x: niv[_x])
        a.set_index([_level], append=c, inplace=True)

    if o is not None:
        time_df = time_df.xs(_context[o], level='Context')
    else:
        time_df = time_df.drop(['Tot', 'Average'], level='Context')
    df = time_df.reset_index(_level, drop=False)
    if _level == 'Level':
        df[_level] = df[_level].map(lambda _x: lvl(_x, b))
    df_level = df[_level].unique()
    df.set_index([_level], append=True, inplace=True)
    time_level_plot(df, df_level, None, ax13, 3, time_ratio, _color3, _level)
    ax13.set_frame_on(False)
    ax13.set_ylabel(_title + '/minute')

    if not c:
        f = a.groupby(level=_level, sort=False).mean()
    else:
        f = a

    sns.heatmap(f.loc[:, 'TileXSize':'DoorNumber'], ax=ax9, cbar=None, annot=False, cmap='vlag', linewidth=0.5)
    sns.heatmap(f.loc[:, 'TileXSize':'DoorNumber'], ax=ax5, cbar=None, annot=True, cmap="vlag", linewidth=0.5)

    locs = ax5.get_xticks()
    labels = ax5.get_xticklabels()
    gh = a.loc[:, 'TileXSize':'DoorNumber']
    gh.columns = locs
    gh = gh.reset_index(level=_level, drop=False)
    if _level == 'Level':
        gh[_level] = gh[_level].apply(lambda x: niv.index(x))
    gh.sort_values(_level, inplace=True)
    if _level == 'Level':
        gh[_level] = gh[_level].apply(lambda x: niv[x])
    gh = gh.melt(id_vars=[_level])
    sns.barplot(x=gh['variable'], y=gh['value'], data=a, hue=gh[_level], ax=ax2, palette=color_set, errwidth=0.5)
    ax2.legend(title=title_suffix, loc=1)
    double_plot(a, study_columns[0], ax10, ax1, study_columns[0], color_set, _level, mapper)
    double_plot(a, study_columns[1], ax11, ax3, study_columns[1], color_set, _level, mapper)
    double_plot(a, study_columns[2], ax12, ax4, study_columns[2], color_set, _level, mapper)
    double_plot(a, study_columns[3], ax16, ax14, study_columns[3], color_set, _level, mapper)

    for study_column, ax in zip(study_columns, [ax6, ax7, ax8, ax15]):
        sns.heatmap(f.loc[:, [study_column]], ax=ax, cbar=None, annot=True, cmap="vlag", fmt=".1f")
        ax.set_yticklabels("")
        ax.set_ylabel(None)

    if c:
        lbl = [item[0] for item in f.index.tolist()]
    else:
        lbl = f.index.tolist()
    ax6.set_yticklabels(lbl, rotation='horizontal')

    ###

    level_length = f.reset_index(_level)[_level].apply(mapper).sort_values().value_counts(sort=False)
    if c:
        x1 = 0.125
        x2 = 0.9
        y1 = 3.9 / grid_height  # 0.435
        y2 = 0.99 / grid_height
        _t = pd.Series([0, 0, 0, 0, 0, 0])
        figlines = []
        # display(level_length.sum())

        # level_length = _t.T.add(level_length, fill_value=0.0, axis=0)
        h_cell = (y1 - y2) / level_length.sum()
        # display(h_cell)
        for i in range(len(color_set)):
            _h_cell = h_cell * (level_length.to_list()[i])
            y2 = y1 - _h_cell + 0.001 * 2
            x = [(x1, x2), (x2, x1), (x1, x1)]
            y = [(y1, y1), (y2, y2), (y2, y1)]
            line = lines.Line2D(x, y, transform=fig.transFigure, c=color_set[i], linewidth=2)
            figlines.append(line)
            y1 = y2 - 0.001 * 2
        fig.lines = figlines

    ax2.set_xlabel(None)
    # ax2.legend(loc='upper left')
    ax2.set_xticklabels("")
    ax2.set_frame_on(False)
    ax2.set_ylabel(None)
    ax5.set_xticklabels(labels, rotation=30, ha="right", rotation_mode='anchor')
    ax9.set_yticklabels("")
    ax5.set_yticklabels("")
    ax5.set_ylabel(None)
    ax9.set_ylabel(None)
    return 1


def order_analysis(a, df, time_df, feedback_df, keep_list, sw, title, survey='B', rorder=3):
    feedback_df2 = feedback_df[feedback_df['Survey'] == survey]
    b = Software.index(sw)
    matplotlib.rcParams['axes.autolimit_mode'] = 'round_numbers'
    matplotlib.rcParams['axes.xmargin'] = 0
    matplotlib.rcParams['axes.ymargin'] = 0
    label = (_context[a - 1])
    df2 = df.xs(label, level='Context')
    df = df.groupby(level=['Name', 'Level', 'Order', 'Context'], sort=False).sum()
    if 'Max' in df.columns:
        df['Max'] = df.loc[:, 'TileXSize':'DoorNumber'].max(axis=1)
    if 'CV' in df.columns:
        df['CV'] = df.loc[:, 'TileXSize':'DoorNumber'].std(axis=1) / df.loc[:, 'TileXSize':'DoorNumber'].mean(axis=1)
    time_ratio = (df2.droplevel('Object')['Time'] / df.xs(label, level='Type').loc[
        df2.drop(0, level='Order').apply((lambda x: x.index.values), axis=0)['Time'].values]['Time'])
    time_ratio = pd.DataFrame(time_ratio.values, index=df2['Time'].index)
    fig = plt.figure(figsize=(24, 12), facecolor="#fefdfd")
    _title = str(_context[a - 1])
    fig.suptitle(_title + ': ' + 'Number of ' + title + " by " + sw + ' level', y=0.94, fontsize=20)
    gs = GridSpec(4, 11, figure=fig, wspace=0.4, hspace=0.2)
    ax1 = fig.add_subplot(gs[:1, 3:6])
    ax2 = fig.add_subplot(gs[1:2, 3:6], sharey=ax1)
    ax3 = fig.add_subplot(gs[2:3, 3:6], sharey=ax1)
    ax4 = fig.add_subplot(gs[:4, :1])
    ax5 = fig.add_subplot(gs[3:4, 3:6])
    ax6 = fig.add_subplot(gs[:4, 1:2])
    ax7 = fig.add_subplot(gs[:4, 2:3])
    ax8 = fig.add_subplot(gs[:1, 9:])
    ax9 = fig.add_subplot(gs[1:2, 9:])
    ax10 = fig.add_subplot(gs[2:3, 9:])
    ax11 = fig.add_subplot(gs[3:4, 9:])
    ax12 = fig.add_subplot(gs[:1, 6:9])
    ax13 = fig.add_subplot(gs[1:2, 6:9], sharey=ax12)
    ax14 = fig.add_subplot(gs[2:3, 6:9], sharey=ax12)
    ax15 = fig.add_subplot(gs[3:4, 6:9])
    result = df.reset_index('Level', drop=False)
    result['Level'] = result['Level'].map(lambda _x: lvl(_x, b))
    result.sort_values('Level', axis=0, inplace=True)
    if 'Time' in result.columns:
        result['Time'] = result['Time'] / 60
        if 'Iterations / Minute' in keep_list:
            result['Iterations / Minute'] = result['Total'] / result['Time']
        if 'Time' not in keep_list:
            result = result.drop(['Time'], axis=1)
    context_feedback = feedback_df2[feedback_df2['Context'] == _context[a - 1]]
    context_feedback['Level'] = context_feedback['Level'].map(lambda _x: lvl(_x, b))
    ax = [ax1, ax2, ax3, ax4, ax6, ax7, ax8, ax9, ax10]

    for i in range(3):
        interaction_line_plot(ax[i], result.xs(label, level='Context'), i + 1, keep_list, _color)
        box_plot(ax[i + 3], i, result, keep_list, label)
        plot_feedback(ax[i + 6], i + 1, context_feedback, _color)
    ax6.set_yticklabels("")
    ax7.set_yticklabels("")
    # matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    df = time_df.xs(_context[a - 1], level='Context').reset_index('Level', drop=False)
    df['Level'] = df['Level'].map(lambda _x: lvl(_x, b))
    df0level = df.xs(1, level='Order')['Level'].unique()
    df1level = df.xs(2, level='Order')['Level'].unique()
    df2level = df.xs(3, level='Order')['Level'].unique()
    df_level = [df0level, df1level, df2level]
    df.set_index(['Level'], append=True, inplace=True)
    ax = [ax12, ax13, ax14]
    for i in range(3):
        time_level_plot(df, df_level, i, ax[i], rorder, time_ratio, _color)
        ax[i].set_ylabel(title + '/minute', labelpad=1)
    df = df.droplevel('Level')
    for i in range(3):
        sns.regplot(x='variable', y='value', data=df.xs(i + 1, level='Order').melt().applymap(lambda x: int(x)),
                    ax=ax15, order=rorder, x_estimator=np.mean, scatter=False, color=_color2[i], ci=None)
    ax15.tick_params(axis='y', pad=-1)
    ax15.set_ylabel(None)
    ax15.set_xlabel(None)
    level_plot = result.xs(label, level='Context').drop(keep_list, axis=1).drop(['Level'], axis=1)
    level_plot = level_plot.reset_index('Order', drop=False)
    level_plot = level_plot.melt(id_vars='Order')
    sns.barplot(x='variable', y='value', data=level_plot, hue='Order', palette='RdYlBu_r', ax=ax5,
                errwidth=0.5)  # , dodge=0.2)
    sns.barplot(x='variable', y='value', data=context_feedback[context_feedback['Survey'] == survey], hue='Order',
                palette='RdYlBu_r', ax=ax11, errwidth=0.5)
    ax11.set_ylabel(None)
    ax11.get_legend().remove()
    ax11.set_xlabel(None)
    ax11.tick_params(axis='x', rotation=20)
    ax11.tick_params(axis='y', pad=-1)
    ax5.legend(loc='upper right')
    ax5.tick_params(axis='y', pad=-1)
    ax5.set_xticklabels("")
    ax5.set_xlabel('Parameter')
    ax5.set_title('Average by Interaction order', loc='left', y=1, pad=3)
    return


def context_reorder(data, choice):
    context_grasshopper = data[(data["Object"] > 1.1) & (data["Object"] < 2)]
    context_hybrid = data[(data["Object"] > 2.1) & (data["Object"] < 3)]
    context_plugin = data[(data["Object"] > 3.1) & (data["Object"] < 4)]
    order1 = context_grasshopper.index[0]
    order2 = context_hybrid.index[0]
    order3 = context_plugin.index[0]
    _order = [_x for _, _x in sorted(zip([order1, order2, order3], [1, 2, 3]))]
    if choice == 0:
        return [context_grasshopper, context_hybrid, context_plugin], ['Grasshopper', 'Hybrid', 'Rhino'], _order
    elif choice == 1:
        return context_grasshopper, 'Grasshopper'
    elif choice == 2:
        return context_hybrid, 'Hybrid'
    elif choice == 3:
        return context_plugin, 'Rhino'


def sub_selection(_context, choice):
    facade_choice = choice
    if facade_choice == 0:
        return _context
    return _context.xs(choice, level='Object', drop_level=False)


def diff_analysis(_context):
    _diff = (_context.diff(1, 0) != 0)
    _diff.iloc[0] = False
    _diff['Time'] = _context['Time']
    return _diff


def timeconvert(time):
    hours = int(time / 3600)
    minutes = int((time - hours * 3600) / 60)
    seconds = int(time - hours * 3600 - minutes * 60)
    return datetime.time(hours, minutes, seconds)


def time_to_sec(time):
    return (time.second + time.minute * 60 + time.hour * 3600) / 60


def split_profile(_df, _imp, _profile):
    prof1 = pd.DataFrame()
    prof2 = pd.DataFrame()
    prof3 = pd.DataFrame()
    _profile_ = _profile.loc[_df.index]
    score = _profile_[_imp]
    it = 0
    for x in score:
        if int(x) == 0:
            prof1 = prof1.append(_df.iloc[it])
        if int(x) == 1:
            prof2 = prof2.append(_df.iloc[it])
        if int(x) == 2:
            prof3 = prof3.append(_df.iloc[it])
        it += 1
    return prof1.T, prof2.T, prof3.T


def plot_feedback(ax, a, _feedback_df, _color, _level='Level'):
    if a is None:
        pass
    else:
        _feedback_df = _feedback_df[_feedback_df['Order'] == a]
    _feedback_df.sort_values(_level, inplace=True)
    if _level == 'Level':
        def mapper(self):
            return niv[int(self)]

        def color(self):
            return _color[int(self)]
    elif _level == 'Context':
        def mapper(self):
            return self

        def color(self):
            return _color[_context.index(self)]
    else:
        def mapper(self):
            return self

        def color(self):
            return _color[self - 1]
    colors = _feedback_df[_level].map(color)
    _feedback_df[_level] = _feedback_df[_level].map(mapper)

    color_set = colors.drop_duplicates().to_list()
    ax.set_autoscaley_on(False)
    ax.set_ybound(0, 11)
    # _feedback_df = _feedback_df[_feedback_df['Survey'] == 'B']
    sns.barplot(x='variable', y='value', data=_feedback_df, order=feedback_col, hue=_level, ci='sd',
                palette=color_set, ax=ax, errwidth=1, capsize=0.2)

    handle, label = ax.get_legend_handles_labels()
    sns.swarmplot(x='variable', y='value', data=_feedback_df, order=feedback_col, hue=_level,
                  palette=color_set, ax=ax, dodge=True, edgecolor="white", linewidth=1, size=7)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_frame_on(False)
    ax.legend(handle, label)
    if a is not None:
        ax.set_xticklabels("")
    ax.tick_params(axis='y', pad=0)
    return


def interaction_line_plot(_ax, result, _order, keep_list, _color):
    int1 = result[result.index.get_level_values('Order') == _order]
    _min = int1.min()
    _max = int1.max()
    _mean1 = int1.mean()
    int1.drop(keep_list, axis=1, inplace=True)
    colors = int1['Level'].map(lambda x: _color[int(x)])
    int1['Level'] = int1['Level'].map(lambda x: niv[int(x)])
    color_set = colors.drop_duplicates().to_list()
    int1 = int1.melt(id_vars=['Level'])
    sns.barplot(x=int1['variable'], y=int1['value'], data=int1, hue=int1['Level'], palette=color_set, ax=_ax,
                errwidth=0.5)
    _ax.set_title('Interaction ' + str(_order), loc='left', pad=3)
    _ax.set_ylabel(None)
    _ax.set_xlabel(None)
    _ax.tick_params(axis='y', pad=-1)
    _ax.legend(loc='upper right', title='Level')
    _ax.set_xticklabels("")
    return int1


def box_plot(ax, c, _r, keep_list, label):
    r = _r.xs(label, level='Context')[[keep_list[c], 'Level']]
    r3 = _r.drop(0, level='Order')[[keep_list[c], 'Level']].reset_index('Order', drop=False)
    r3['Order'] = 4
    r = r.reset_index('Order', drop=False)
    r2 = r.copy()
    color_palette = sns.mpl_palette('RdYlBu_r', 3)
    color_palette.append('gray')
    r2['Order'] = 4
    r = r.append(r2)
    ax.locator_params(axis='x', nbins=3, prune=None)
    # ax.set_xlim(left=0, auto=None)
    colors = r['Level'].map(lambda x: _color[int(x)])
    color_set = colors.drop_duplicates().to_list()
    inv = sns.boxplot(ax=ax, y='Order', x=keep_list[c], data=r3, orient='h', hue='Order', dodge=False,
                      palette=color_palette)
    t = inv.get_children()
    for thing in t:
        try:
            thing.remove()
        except:
            pass
    sns.boxplot(ax=ax, y='Order', x=keep_list[c], data=r, orient='h', hue='Order', dodge=False, palette=color_palette)
    sns.swarmplot(ax=ax, y='Order', x=keep_list[c], data=r, orient='h', hue='Level', palette=color_set, s=10,
                  dodge=True, marker='x', linewidth=3)
    ax.set_title(keep_list[c], loc='center', pad=3)
    # ax.set_xlim(left=0, auto=None)
    ax.get_legend().remove()
    ax.set_ylabel(None)
    ax.grid(visible=True)
    ax.set_yticklabels(['Interaction 1', 'Interaction 2', 'Interaction 3', 'Average'])
    return


def time_level_plot(_df, df_level, order_choice, ax, regression_order, _time_ratio, _color, _level='Level'):
    if order_choice is None:
        # _df = _df.droplevel('Order')
        level_list = df_level
    else:
        _df = _df.xs((order_choice + 1), level='Order')
        level_list = df_level[order_choice]
    ratio_1 = _time_ratio.xs(2, level='Object').mean().values[0]
    ratio_2 = _time_ratio.xs(3, level='Object').mean().values[0]
    ratio_3 = _time_ratio.xs(4, level='Object').mean().values[0]
    ratio = np.array([ratio_1, ratio_2, ratio_3])
    cum_ratio = np.cumsum(ratio)
    cum_ratio = cum_ratio - ratio
    i = 0
    for _lvl in level_list:
        if _level != 'Level':
            _lvl_ = i
        else:
            _lvl_ = _lvl
        for facade in range(3):
            _df_ = _df.xs(facade + 2, level='Object')

            def mapper(self):
                return (int(self) * ratio[facade]) + cum_ratio[facade] * 10

            _df_ = _df_.rename(columns=mapper)
            level_df = _df_.xs(_lvl, level=_level).melt()
            sns.regplot(x='variable', y='value', data=level_df, color=_color[_lvl_], ax=ax, order=regression_order,
                        scatter=False, ci=50)
        i += 1
    ax.set_xticks(cum_ratio * 10 + ratio * 5)
    ax.set_xticklabels(['Facade 1', 'Facade 2', 'Facade 3'])
    ax.set_ybound(lower=0)
    ax.set_title("Rate/Time", loc="left", pad=-5)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', pad=1)
    return


def convert_subject_level(n):
    _level = ["Aucune expérience", "Novice", "Limité", "Habitué", "Avancé", "Expert"]
    return _level.index(n)


def lvl(self, b):
    return int(str(self)[b])


def profile(n):
    low = n.quantile(q=0.33)
    high = n.quantile(q=0.66)
    p = []
    for x in n:
        if x <= low:
            p.append(0)
        elif low < x <= high:
            p.append(1)
        elif high < x:
            p.append(2)
    return p


def double_plot(df, clname, ax1, ax2, title, color_list, _level, fn, _color='#bde0fe'):
    time = df[clname]
    time = time.reset_index(level=_level)
    time['x'] = title
    ax1.margins(y=0.1)
    time[_level] = time[_level].map(fn)
    time['hue'] = time[_level].apply(lambda x: x > 2.5)
    # display(time)
    r = sns.regplot(x=time[_level], y=time[clname], ax=ax1, x_estimator=np.mean, order=1, truncate=False)
    _markers = r.get_children()
    _markers[0].set_facecolors(color_list)
    _lines = r.get_lines()
    it = 0
    for line in _lines[:-1]:
        line.set_color(color_list[it])
        it += 1
        line.set_zorder(3)
    _markers[0].set_zorder(4)
    ax1.set_xticklabels("")
    _dodge = False
    _hue = None
    _order = range(3)
    if _level == 'Level':
        ax1.set_xbound(lower=0, upper=5)
        _dodge = True
        _hue = 'hue'
        _order = range(6)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='x', length=0)
    ax1.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    if ax2 is not None:
        ax3 = ax2.twiny()
        sns.violinplot(x='x', y=time[clname], data=time, hue=_hue, hue_order=[False, True], ax=ax2, inner='quartile',
                       color='#EDF6F9', alpha=0.2, zorder=1, cut=0, positions=[2], split=_dodge, palette=['#EDF6F9'])
        sns.swarmplot(x=_level, y=time[clname], data=time, order=_order, hue=time[_level], ax=ax3, palette=color_list,
                      edgecolor="grey",
                      linewidth=0.4, dodge=False, s=7)
        ax3.get_legend().remove()
        if _dodge:
            try:
                ax2.get_legend().remove()
            except:
                pass
        ax2.set_xticklabels("")
        ax2.set_frame_on(False)
        ax3.set_xticklabels("")
        ax3.set_frame_on(False)
        ax2.grid(visible=True)
        ax2.set_ylabel(None)
        ax2.set_xlabel(None)
        ax3.set_ylabel(None)
        ax3.set_xlabel(None)

    ax1.set_frame_on(False)
    ax1.set_ylabel(None)
    ax1.set_xlabel(None)
    ax1.set_title(title)
    return 1


def choose_level(_df, b, _level='Level'):
    _df = _df.reset_index(level=_level)
    if _level == 'Level':
        _df['Level'] = _df['Level'].map(lambda x: int(str(x)[b]))
    level_length = _df[_level].value_counts().sort_index()
    _df.set_index([_level], append=True, inplace=True)
    _df.sort_index(axis=0, level=_level, inplace=True)
    return _df, level_length


def context_analysis(a, df, time_df, study_columns, sw='Average', title='Title', y2=0.190, rorder=3, _level='Level'):
    b = Software.index(sw)
    df = df.xs(_context[a], level='Context')
    it2 = df.groupby(level=['Name', 'Level', 'Order'], sort=False).sum()
    time_ratio = (df.droplevel('Object')['Time'] /
                  it2.loc[df.apply((lambda _x: _x.index.values), axis=0)['Time'].values]['Time'])
    time_ratio = pd.DataFrame(time_ratio.values, index=df['Time'].index)

    if 'Time' in it2.columns:
        it2['Time'] = it2['Time'] / 60
        if 'Iterations / Minute' in study_columns:
            it2['Iterations / Minute'] = (it2['Total'] / it2['Time']).round(0)
        if 'Time' not in study_columns:
            it2 = it2.drop(['Time'], axis=1)
    if 'Max' in it2.columns:
        it2['Max'] = it2.loc[:, 'TileXSize':'DoorNumber'].max(axis=1)
    if 'CV' in it2.columns:
        it2['CV'] = it2.loc[:, 'TileXSize':'DoorNumber'].std(axis=1) / it2.loc[:, 'TileXSize':'DoorNumber'].mean(axis=1)
    it2, level_length = choose_level(it2, b, _level)

    it = it2[study_columns]
    it2 = it2.loc[:, 'TileXSize':'DoorNumber']
    fig = plt.figure(figsize=(22, 9), facecolor="#fefdfd")
    _Title = str(_context[a])
    fig.title = str(title)
    gs = GridSpec(7, 24, figure=fig, wspace=3.5, hspace=0.3)
    ax1 = fig.add_subplot(gs[1:4, :3])
    ax3 = fig.add_subplot(gs[1:4, 3:6])
    ax4 = fig.add_subplot(gs[1:4, 6:9])
    ax14 = fig.add_subplot(gs[1:4, 9:12])
    ax9 = fig.add_subplot(gs[4:, 12:])
    ax5 = fig.add_subplot(gs[4:, 12:])
    ax2 = fig.add_subplot(gs[2:4, 12:], sharex=ax9)
    ax6 = fig.add_subplot(gs[4:, :3])
    ax7 = fig.add_subplot(gs[4:, 3:6])
    ax8 = fig.add_subplot(gs[4:, 6:9])
    ax15 = fig.add_subplot(gs[4:, 9:12])
    ax10 = fig.add_subplot(gs[:1, :3])
    ax11 = fig.add_subplot(gs[:1, 3:6])
    ax12 = fig.add_subplot(gs[:1, 6:9])
    ax16 = fig.add_subplot(gs[:1, 9:12])
    ax13 = fig.add_subplot(gs[:2, 12:])
    # ax14 = fig.add_subplot(gs[:1, :12])
    sns.heatmap(it2.droplevel(['Order', 'Level']), annot=True, ax=ax5, cbar=False, cmap="vlag", linewidth=0.5,
                fmt=".1f")
    ax5.set_yticklabels("")
    ax5.set_ylabel(None)
    ax9.set_yticklabels("")
    ax9.set_ylabel(None)
    ax9.set_xticklabels("")
    ax9.set_xlabel(None)
    locs = ax5.get_xticks()
    ax2.set_xticks(locs)
    time = pd.DataFrame(it[study_columns[0]].droplevel(['Level', 'Order']))
    ax9.tick_params(axis='y', tickdir='in')
    tot_it = pd.DataFrame(it[study_columns[1]])
    sns.heatmap(time, ax=ax6, cbar=False, annot=True, cmap="vlag", fmt='.1f')
    sns.heatmap(tot_it, ax=ax7, cbar=False, annot=True, cmap="vlag", fmt=".1f")
    ax7.set_yticklabels("")
    ax7.set_ylabel(None)
    ax7.set_xticklabels("")
    ax7.set_xlabel(study_columns[1])
    it_min = pd.DataFrame(it[study_columns[2]])
    sns.heatmap(it_min, ax=ax8, cbar=False, annot=True, cmap="vlag", fmt='.1f')
    ax8.set_yticklabels("")
    ax8.set_ylabel(None)
    ax8.set_xticklabels("")
    ax8.set_xlabel(study_columns[2])
    it_min2 = pd.DataFrame(it[study_columns[3]])
    sns.heatmap(it_min2, ax=ax15, cbar=False, annot=True, cmap="vlag", fmt='.1f')
    ax15.set_yticklabels("")
    ax15.set_ylabel(None)
    ax15.set_xticklabels("")
    ax15.set_xlabel(study_columns[3])

    if _level == 'Order':
        level_plot_df = it2.droplevel(['Level'])
    else:
        level_plot_df = it2.droplevel(['Order'])

    level_plot_df.columns = locs
    colors = sns.mpl_palette("Paired", 6)
    level_plot_df = level_plot_df.reset_index(level=_level, drop=False)
    color_set = level_plot_df[_level].map(lambda _x: colors[_x])
    color_set = color_set.drop_duplicates().to_list()
    # levels = ['No experience', 'Novice', 'Limited', 'Basic', 'Advanced', 'Expert']
    if _level == 'Level':
        def mapper(self):
            return niv[self]
    else:
        def mapper(self):
            return self
    level_plot_df[_level] = level_plot_df[_level].map(mapper)
    ax2lines = ax2.get_lines()
    _it = 0
    for line in ax2lines:
        line.set_color(color_set[_it])
        line.set_linewidth(0.5)
        _it += 1
    level_plot_df = level_plot_df.melt(id_vars=_level)
    sns.barplot(x='variable', y='value', hue=_level, palette=color_set, data=level_plot_df, ax=ax2, errwidth=0.5)

    double_plot(it, study_columns[0], ax10, ax1, study_columns[0], color_set, _level, (lambda _x: int(_x)), _color)
    double_plot(it, study_columns[1], ax11, ax3, study_columns[1], color_set, _level, (lambda _x: _x), _color)
    double_plot(it, study_columns[2], ax12, ax4, study_columns[2], color_set, _level, (lambda _x: _x), _color)
    double_plot(it, study_columns[3], ax16, ax14, study_columns[3], color_set, _level, (lambda _x: _x), _color)

    df = time_df.xs(_context[a], level='Context').reset_index(_level, drop=False)
    if _level == 'Level':
        df[_level] = df[_level].map(lambda _x: lvl(_x, b))
    df_level = df[_level].unique()
    # display(df_level)
    df.set_index([_level], append=True, inplace=True)
    time_level_plot(df, df_level, None, ax13, rorder, time_ratio, colors, _level)
    ax13.set_frame_on(False)
    ax13.set_ylabel(title + '/minute')
    ltitle = _level
    if _level == 'Level':
        ltitle = sw + ' level'
    fig.suptitle(_Title + ': ''Number of ' + title + " by " + ltitle, fontsize=20, y=0.95)

    x1 = 0.125
    x2 = 0.9
    y1 = 0.435
    _t = pd.Series([0, 0, 0, 0, 0, 0])
    figlines = []
    level_length = _t.T.add(level_length, fill_value=0.0, axis=0)
    h_cell = (y1 - y2) / (len(it[study_columns[0]]) - 3)
    if 0 in df_level:
        _h_cell = h_cell * (level_length.loc[0])
        y2 = y1 - _h_cell + 0.001 * 2
        x = [(x1, x2), (x2, x1), (x1, x1)]
        y = [(y1, y1), (y2, y2), (y2, y1)]
        line1 = lines.Line2D(x, y, transform=fig.transFigure, c=colors[0], linewidth=2)
        figlines.append(line1)
        y1 = y2 - 0.001 * 2
    if 1 in df_level:
        _h_cell = h_cell * (level_length.loc[1])
        y2 = y1 - _h_cell + 0.001 * 2
        x = [(x1, x2), (x2, x1), (x1, x1)]
        y = [(y1, y1), (y2, y2), (y2, y1)]
        line2 = lines.Line2D(x, y, transform=fig.transFigure, c=colors[1], linewidth=2)
        figlines.append(line2)
        y1 = y2 - 0.001 * 2
    if 2 in df_level:
        _h_cell = h_cell * (level_length.loc[2])
        y2 = y1 - _h_cell + 0.001 * 2
        x = [(x1, x2), (x2, x1), (x1, x1)]
        y = [(y1, y1), (y2, y2), (y2, y1)]
        line3 = lines.Line2D(x, y, transform=fig.transFigure, c=colors[2], linewidth=2)
        figlines.append(line3)
        y1 = y2 - 0.001 * 2
    if 3 in df_level:
        _h_cell = h_cell * (level_length.loc[3])
        y2 = y1 - _h_cell + 0.001 * 2
        x = [(x1, x2), (x2, x1), (x1, x1)]
        y = [(y1, y1), (y2, y2), (y2, y1)]
        line4 = lines.Line2D(x, y, transform=fig.transFigure, c=colors[3], linewidth=2)
        figlines.append(line4)
        y1 = y2 - 0.001 * 2
    if 4 in df_level:
        _h_cell = h_cell * (level_length.loc[4])
        y2 = y1 - _h_cell + 0.001 * 2
        x = [(x1, x2), (x2, x1), (x1, x1)]
        y = [(y1, y1), (y2, y2), (y2, y1)]
        line5 = lines.Line2D(x, y, transform=fig.transFigure, c=colors[4], linewidth=2)
        figlines.append(line5)
        y1 = y2 - 0.001 * 2
    if 5 in df_level:
        _h_cell = h_cell * (level_length.loc[5])
        y2 = y1 - _h_cell + 0.001 * 2
        x = [(x1, x2), (x2, x1), (x1, x1)]
        y = [(y1, y1), (y2, y2), (y2, y1)]
        line6 = lines.Line2D(x, y, transform=fig.transFigure, c=colors[5], linewidth=2)
        figlines.append(line6)
    fig.lines = figlines
    ax2.set_frame_on(False)
    ax2.set_xlabel(None)
    ax2.legend(title=ltitle, loc=1)
    h, label = ax2.get_legend_handles_labels()
    ax2.tick_params(axis='y', tickdir='in')
    ax2.tick_params(axis='x', tickdir='out')
    ax5.tick_params(axis='x', tickdir='out', top=True)
    label = ax5.get_xticklabels()
    ax5.set_xticklabels(label, rotation=45, ha="right", rotation_mode='anchor')
    ax2.set_ylabel(None)
    ax2.set_xticklabels("")
    ax6.set_ylabel(None)
    ax12.set_frame_on(False)
    ax12.set_ylabel(None)
    ax12.set_xlabel(None)
    fig2 = plt.figure(figsize=(13.2, 4), facecolor="#fefdfd", dpi=200)
    axes = fig2.add_subplot()
    time_level_plot(df, df_level, None, axes, rorder, time_ratio, _color, _level)
    axes.set_frame_on(False)
    axes.legend(h, label, title=(sw + " level"), loc=1)
    fig2.suptitle('Number of ' + title + ": " + _Title, fontsize=20, y=0.92)
    axes.set_ylabel(title + '/minute')
    plt.savefig('output/' + title + '-' + _Title + '-' + 'rate-by' + sw + '.png')
    plt.delaxes(axes)
    plt.close(fig2)
    plt.figure(fig)
    return 1


def feedback(feedback_df, context_index, sw, survey='B', _level='Level'):
    b = Software.index(sw)
    l = ['A', 'B']
    survey_order = ['after each interaction ', 'at end of experiment ']
    if survey is not None:
        feedback_df = feedback_df[feedback_df['Survey'] == survey]
        fig = plt.figure(figsize=(12, 4), facecolor="#fefefe", dpi=200)
        ax = fig.add_subplot()
    else:
        fig = plt.figure(figsize=(22, 4), facecolor="#fefefe", dpi=200)
        ax = [fig.add_subplot(1, 2, 1), fig.add_subplot(1, 2, 2)]
    if _level == 'Level':
        ltitle = sw + ' level '
        color = _color
    else:
        ltitle = _level
        color = _color2
    if context_index is None:
        title_2 = 'Survey data '
    else:
        title_2 = _context[context_index] + ' survey data '
    if context_index is not None:
        context_feedback = feedback_df[feedback_df['Context'] == _context[context_index]]
    else:
        context_feedback = feedback_df[feedback_df['Order'] != 0]
    context_feedback['Level'] = context_feedback['Level'].map(lambda _x: lvl(_x, b))
    if survey is not None:
        plot_feedback(ax, None, context_feedback, color, _level)
        fig.suptitle(title_2 + survey_order[l.index(survey)] + 'by ' + ltitle, fontsize=16, y=0.92)
    else:
        plot_feedback(ax[0], None, context_feedback[context_feedback['Survey'] == 'A'], color, _level)
        ax[0].set_title(title_2 + survey_order[0], loc='center', size=10, y=0.92)
        plot_feedback(ax[1], None, context_feedback[context_feedback['Survey'] == 'B'], color, _level)
        ax[1].set_title(title_2 + survey_order[1], loc='center', size=10, y=0.92)
        fig.suptitle(title_2 + 'by ' + ltitle, fontsize=16, y=0.95)
# %%
