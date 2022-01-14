import numpy as np
import pandas as pd
import datetime
import seaborn as sns
from matplotlib import lines
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


_type=['Grasshopper', 'Hybrid', 'Plugin']
niv=['No experience','Novice','Limited','Basic','Advanced','Expert']
_color=sns.mpl_palette('Paired',5)
_color2=sns.mpl_palette('RdYlBu_r',3)

def order_analysis(a, df, time_df, feedback_df, keep_list, b, title):
    label=(_type[a - 1])
    df2=df.xs(label,level='Type')
    df=df2.groupby(level=['Name','Level','Order'],sort=False).sum()
    time_ratio=(df2.droplevel('Object')['Time']/df.loc[df2.drop(0,level='Order').apply((lambda x:x.index.values),axis=0)['Time'].values]['Time'])
    time_ratio=pd.DataFrame(time_ratio.values,index=df2['Time'].index)
    fig=plt.figure(figsize=(24,12))
    _title=str(_type[a - 1])
    fig.suptitle(title + ": " + _title, y=0.94, fontsize=20)
    gs = GridSpec(4,12,figure=fig)
    ax1=fig.add_subplot(gs[:1,3:6])
    ax2=fig.add_subplot(gs[1:2,3:6])
    ax3=fig.add_subplot(gs[2:3,3:6])
    ax4=fig.add_subplot(gs[:4,:1])
    ax5=fig.add_subplot(gs[3:4,3:6])
    ax6=fig.add_subplot(gs[:4,1:2])
    ax7=fig.add_subplot(gs[:4,2:3])
    ax8=fig.add_subplot(gs[:1,9:])
    ax9=fig.add_subplot(gs[1:2,9:])
    ax10=fig.add_subplot(gs[2:3,9:])
    ax11=fig.add_subplot(gs[3:4,9:])
    ax12=fig.add_subplot(gs[:1,6:9])
    ax13=fig.add_subplot(gs[1:2,6:9])
    ax14=fig.add_subplot(gs[2:3,6:9])
    ax15=fig.add_subplot(gs[3:4,6:9])
    keep_list=keep_list
    result=df.reset_index('Level',drop=False)
    result['Level']=result['Level'].map(lambda x:x[b])
    result.sort_values('Level',axis=0,inplace=True)
    if 'Time' in result.columns:
        result['Time']=result['Time']/60
        if 'Time' not in keep_list:
            result=result.drop(['Time'],axis=1)
    context_feedback=feedback_df[feedback_df['Type'] == _type[a - 1]]
    context_feedback['Level']=context_feedback['Level'].map(lambda x:x[b])
    ax=[ax1,ax2,ax3,ax4,ax6,ax7,ax8,ax9,ax10]
    for i in range(3):
        interaction_line_plot(ax[i], result, i+1, keep_list,_color,niv)
        box_plot(ax[i + 3], i, result, keep_list)
        plot_feedback(ax[i + 6], i+1, context_feedback,_color,niv)
    ax6.set_yticklabels("")
    ax7.set_yticklabels("")
    df=time_df.xs(_type[a - 1], level='Type').reset_index('Level', drop=False)
    df['Level']=df['Level'].map(lambda x:int(x[b]))
    df0level=df.xs(1,level='Order')['Level'].unique()
    df1level=df.xs(2,level='Order')['Level'].unique()
    df2level=df.xs(3,level='Order')['Level'].unique()
    df_level=[df0level,df1level,df2level]
    df.set_index(['Level'],append=True,inplace=True)
    ax=[ax12,ax13,ax14]
    for i in range(3):
        time_level_plot(df, df_level, i, ax[i], 3,time_ratio,_color)
    df=df.droplevel('Level')
    for i in range(3):
        sns.regplot(x='variable',y='value',data=df.xs(i+1,level='Order').melt().applymap(lambda x:int(x)),ax=ax15,order=3,x_estimator=np.mean,scatter=False,color=_color2[i],ci=None)
    ax15.tick_params(axis='y',pad=-1)
    ax15.set_ylabel(None)
    ax15.set_xlabel(None)
    level_plot=result.drop(keep_list,axis=1).drop(['Level'],axis=1)
    level_plot=level_plot.reset_index('Order',drop=False)
    level_plot=level_plot.melt(id_vars='Order')
    sns.pointplot(x='variable',y='value',data=level_plot,hue='Order',palette='RdYlBu_r',ax=ax5,ci='sd',dodge=0.2)
    sns.pointplot(x='variable',y='value',data=context_feedback[context_feedback['Survey']=='B'],hue='Order',ci='sd',dodge=0.15,palette='RdYlBu_r',ax=ax11)
    ax11.set_ylabel(None)
    ax11.get_legend().remove()
    ax11.set_xlabel(None)
    ax11.tick_params(axis='x',rotation=20)
    ax11.tick_params(axis='y',pad=-1)
    ax5.legend(loc='upper right')
    ax5.tick_params(axis='y',pad=-1)
    ax5.set_xticklabels("")
    ax5.set_xlabel('Parameter')
    ax5.set_title('Average by Interaction order',loc='left',y=1,pad=3)
    return


def context_reorder(data, choice):
    context_grasshopper = data[(data["Object"]>1.1) & (data["Object"]<2)]
    context_hybrid = data[(data["Object"]>2.1) & (data["Object"]<3)]
    context_plugin = data[(data["Object"]>3.1) & (data["Object"]<4)]
    order1=context_grasshopper.index[0]
    order2=context_hybrid.index[0]
    order3=context_plugin.index[0]
    _order=[_x for _, _x in sorted(zip([order1, order2, order3], [1, 2, 3]))]
    if choice==0:
        return [context_grasshopper,context_hybrid,context_plugin], ['Grasshopper','Hybrid','Plugin'], _order
    elif choice==1:
        return context_grasshopper,'Grasshopper'
    elif choice==2:
        return context_hybrid,'Hybrid'
    elif choice==3:
        return context_plugin,'Plugin'

def sub_selection(_context, choice):
    facade_choice=choice
    if facade_choice==0:
        return _context
    return _context.xs(choice,level='Object',drop_level=False)

def diff_analysis(_context):
    _diff=(_context.diff(1, 0) != 0)
    _diff.iloc[0]=False
    _diff['Time']=_context['Time']
    return _diff

def timeconvert(time):
    hours=int(time / 3600)
    minutes=int((time - hours * 3600) / 60)
    seconds=int(time - hours * 3600 - minutes * 60)
    return datetime.time(hours,minutes,seconds)

def time_to_sec(time):
    return (time.second + time.minute * 60 + time.hour * 3600) / 60

def split_profile(_df, _imp,profile):
    prof1=pd.DataFrame()
    prof2=pd.DataFrame()
    prof3=pd.DataFrame()
    _profile = profile.loc[_df.index]
    score=_profile[_imp]
    it=0
    for x in score:
        if int(x)==0:
            prof1=prof1.append(_df.iloc[it])
        if int(x)==1:
            prof2=prof2.append(_df.iloc[it])
        if int(x)==2:
            prof3=prof3.append(_df.iloc[it])
        it+=1
    return prof1.T,prof2.T,prof3.T

def plot_feedback(ax, a, _feedback_df,_color,niv):
    if a is None:
        pass
    else:
        _feedback_df=_feedback_df[_feedback_df['Order'] == a]
    colors=_feedback_df['Level'].map(lambda x:_color[int(x)])
    _feedback_df['Level']=_feedback_df['Level'].map(lambda x:niv[int(x)])
    color_set=colors.drop_duplicates().to_list()
    ax.set_autoscaley_on(False)
    ax.set_ybound(0,11)
    r=sns.pointplot(x='variable', y='value', data=_feedback_df[_feedback_df['Survey'] == 'A'], hue='Level', ci='sd', dodge=0.3, palette=color_set, markers='x', ax=ax, linestyles='--')

    _lines=r.get_lines()
    for line in _lines[:]:
        line.set_alpha(0.6)
        line.set_linewidth(1.5)
        line.set_zorder(1)

    sns.pointplot(x='variable', y='value', data=_feedback_df[_feedback_df['Survey'] == 'B'], hue='Level', ci='sd', dodge=0.3, palette=color_set, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    if a is not None:
        ax.set_xticklabels("")
    ax.get_legend().remove()
    ax.tick_params(axis='y',pad=-1)
    return

def interaction_line_plot(_ax, result, _order, keep_list, _color, niv):
    int1=result[result.index.get_level_values('Order') == _order]
    _min=int1.min()
    _max=int1.max()
    _mean1=int1.mean()
    int1.drop(keep_list, axis=1, inplace=True)
    colors=int1['Level'].map(lambda x:_color[int(x)])
    int1['Level']=int1['Level'].map(lambda x:niv[int(x)])
    color_set=colors.drop_duplicates().to_list()
    int1=int1.melt(id_vars=['Level'])
    sns.pointplot(x=int1['variable'],y=int1['value'],data=int1,hue=int1['Level'],palette=color_set,ax=_ax,ci='sd',dodge=0.2)
    _ax.set_title('Interaction ' + str(_order), loc='left', pad=3)
    _ax.set_ylabel(None)
    _ax.set_xlabel(None)
    _ax.tick_params(axis='y',pad=-1)
    _ax.legend(loc='upper right',title='Level')
    _ax.set_xticklabels("")
    return int1

def box_plot(ax, c, r, keep_list):
    r=r[[keep_list[c], 'Level']]
    r=r.reset_index('Order',drop=False)
    r2=r.copy()
    color_palette=sns.mpl_palette('RdYlBu_r',3)
    color_palette.append('gray')
    r2['Order']=4
    r=r.append(r2)
    sns.boxplot(ax=ax, y='Order', x=keep_list[c], data=r, orient='h', hue='Order', dodge=False, palette=color_palette)
    sns.swarmplot(ax=ax, y='Order', x=keep_list[c], data=r, orient='h', hue='Level', palette='Paired', dodge=True, s=10, marker='x', linewidth=3)
    ax.set_title(keep_list[c], loc='center', pad=3)
    ax.get_legend().remove()
    ax.set_ylabel(None)
    ax.set_yticklabels(['Interaction 1','Interaction 2','Interaction 3','Average'])
    return

def time_level_plot(_df, df_level, order_choice, ax, regression_order,_timeratio,_color):
    if order_choice is None:
        _df=_df.droplevel('Order')
        level_list=df_level
    else:
        _df=_df.xs((order_choice+1), level='Order')
        level_list=df_level[order_choice]
    ratio_1=_timeratio.xs(2,level='Object').mean().values[0]
    #display(ratio_1)
    ratio_2=_timeratio.xs(3,level='Object').mean().values[0]
    #display(ratio_2)
    ratio_3=_timeratio.xs(4,level='Object').mean().values[0]
    #display(ratio_3)
    #display(ratio_1+ratio_2+ratio_3)
    ratio=[ratio_1,ratio_2,ratio_3]
    cum_ratio=np.cumsum(ratio)
    cum_ratio=cum_ratio-ratio
    for lvl in level_list:
        for facade in range(3):
            _df_=_df.xs(facade+2,level='Object')
            def mapper(self):
                #display(((self*ratio[facade])[0]+sum(ratio[:facade])))
                return (self*ratio[facade])+cum_ratio[facade]*10
            _df_=_df_.rename(columns=mapper)
            level_df=_df_.xs(lvl,level='Level').melt()
            sns.regplot(x='variable', y='value', data=level_df, color=_color[lvl], ax=ax, order=regression_order, x_estimator=np.mean, scatter=False, ci=None)
    ax.set_ylabel(None)
    ax.set_xticklabels("")
    ax.set_xlabel(None)
    ax.tick_params(axis='y',pad=-1)
    return

def convert_subject_level(n):
    _level=["Aucune expérience","Novice","Limité","Habitué","Avancé","Expert"]
    return _level.index(n)


def profile(n):
    low=n.quantile(q=0.33)
    high=n.quantile(q=0.66)
    p=[]
    for x in n:
        if x <= low:
            p.append(0)
        elif low<x<=high:
            p.append(1)
        elif high<x:
            p.append(2)
    return p

def double_plot(df, clname, ax1, ax2, title, color_list, _level, fn, _color='#bde0fe'):

    time=df[clname]
    time=time.reset_index(level=_level)
    time['x']=title
    ax1.margins(y=0.1)
    r=sns.regplot(x=time[_level].map(fn),y=time[clname],ax=ax1,x_estimator=np.mean,order=2)
    _markers=r.get_children()
    _markers[0].set_facecolors(color_list)
    _lines=r.get_lines()
    it=0
    for line in _lines[:-1]:
        line.set_color(color_list[it])
        it+=1
        line.set_zorder(3)
    _markers[0].set_zorder(4)
    ax1.set_xticklabels("")
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='x',length=0)

    if ax2 is not None:
        sns.violinplot(x='x',y=time[clname],data=time,ax=ax2,positions=[2],inner='quartile',cut=0,color='#EDF6F9',alpha=0.2,zorder=1)
        sns.swarmplot(x='x', y=time[clname], data=time, hue=time[_level], ax=ax2, palette=color_list, edgecolor="grey", linewidth=0.4, dodge=True, s=7)
        ax2.get_legend().remove()
        ax2.set_xticklabels("")
        ax2.set_frame_on(False)
        ax2.grid(visible=True)
        ax2.set_ylabel(None)
        ax2.set_xlabel(None)

    ax1.set_frame_on(False)
    ax1.set_ylabel(None)
    ax1.set_xlabel(None)
    return 1
def choose_level(_df, b):
    _df=_df.reset_index(level='Level')
    _df['Level']=_df['Level'].map(lambda x:int(x[b]))
    level_length=_df['Level'].value_counts().sort_index()
    _df.set_index(['Level'],append=True,inplace=True)
    _df.sort_index(axis=0,level='Level',inplace=True)
    return _df,level_length

def context_analysis(a, df, time_df, feedback_df, study_columns, b, title, y2=0.175):
    df=df.xs(_type[a], level='Type')
    it2=df.groupby(level=['Name','Level','Order'],sort=False).sum()
    time_ratio=(df.droplevel('Object')['Time']/it2.loc[df.drop(0,level='Order').apply((lambda x:x.index.values),axis=0)['Time'].values]['Time'])
    time_ratio=pd.DataFrame(time_ratio.values,index=df['Time'].index)
    if 'Time' in it2.columns:
        it2['Time']=it2['Time']/60
        if 'Time' not in study_columns:
            it2=it2.drop(['Time'],axis=1)
    it2,level_length = choose_level(it2, b)
    it=it2[study_columns]
    it2=it2.drop(study_columns, axis=1)
    fig=plt.figure(figsize=(22,12),facecolor="#fefdfd")
    _Title=str(_type[a])
    fig.title=str(title)
    gs = GridSpec(6,30,figure=fig)
    ax1=fig.add_subplot(gs[2:4,:3])
    ax3=fig.add_subplot(gs[2:4,4:7])
    ax4=fig.add_subplot(gs[2:4,8:11])
    ax9=fig.add_subplot(gs[4:,12:])
    ax5=fig.add_subplot(gs[4:,12:])
    ax2=fig.add_subplot(gs[2:4,12:],sharex=ax9)
    ax6=fig.add_subplot(gs[4:,:3])
    ax7=fig.add_subplot(gs[4:,4:7])
    ax8=fig.add_subplot(gs[4:,8:11])
    ax10=fig.add_subplot(gs[1:2,:3])
    ax11=fig.add_subplot(gs[1:2,4:7])
    ax12=fig.add_subplot(gs[1:2,8:11])
    ax13=fig.add_subplot(gs[:2,12:30])
    ax14=fig.add_subplot(gs[:1,:12])

    sns.heatmap(it2.droplevel(['Order','Level']),annot=True,ax=ax5,cbar=False,cmap="vlag",linewidth=0.5)
    ax5.set_yticklabels("")
    ax5.set_ylabel(None)
    ax9.set_yticklabels("")
    ax9.set_ylabel(None)
    ax9.set_xticklabels("")
    ax9.set_xlabel(None)
    locs=ax5.get_xticks()
    ax2.set_xticks(locs)
    time=pd.DataFrame(it[study_columns[0]].droplevel(['Level', 'Order']))
    ax9.tick_params(axis='y',tickdir='in')
    tot_it=pd.DataFrame(it[study_columns[1]])
    sns.heatmap(time,ax=ax6,cbar=False,annot=True,cmap="vlag")
    sns.heatmap(tot_it,ax=ax7,cbar=False,annot=True,cmap="vlag",fmt="g")
    ax7.set_yticklabels("")
    ax7.set_ylabel(None)
    ax7.set_xticklabels("")
    ax7.set_xlabel(study_columns[1])
    it_min=pd.DataFrame(it[study_columns[2]])
    sns.heatmap(it_min,ax=ax8,cbar=False,annot=True,cmap="vlag")
    ax8.set_yticklabels("")
    ax8.set_ylabel(None)
    ax8.set_xticklabels("")
    ax8.set_xlabel(study_columns[2])

    level_plot_df=it2.droplevel(['Order'])

    level_plot_df.columns=locs
    colors=sns.mpl_palette("Paired",6)
    level_plot_df=level_plot_df.reset_index(level='Level',drop=False)
    color_set=level_plot_df['Level'].map(lambda _x:colors[_x])
    color_set=color_set.drop_duplicates().to_list()
    levels=['No experience','Novice','Limited','Basic','Advanced','Expert']
    level_plot_df['Level']=level_plot_df['Level'].map(lambda _x:levels[_x])
    ax2lines=ax2.get_lines()
    _it=0
    for line in ax2lines:
        line.set_color(color_set[_it])
        line.set_linewidth(0.5)
        _it+=1
    level_plot_df=level_plot_df.melt(id_vars='Level')
    sns.pointplot(x='variable',y='value',hue='Level',palette=color_set,data=level_plot_df,ax=ax2,dodge=0.5)

    context_feedback=feedback_df[feedback_df['Type'] == _type[a - 1]]
    context_feedback['Level']=context_feedback['Level'].map(lambda _x:_x[b])
    plot_feedback(ax14, None, context_feedback,_color,niv)
    ax14.set_frame_on(False)

    double_plot(it, study_columns[0], ax10, ax1, 'Time in minutes', color_set, 'Level', (lambda _x:_x), _color)
    double_plot(it, study_columns[1], ax11, ax3, 'Iterations', color_set, 'Level', (lambda _x:_x), _color)
    double_plot(it, study_columns[2], ax12, ax4, 'Iterations/Minute', color_set, 'Level', (lambda _x:_x), _color)

    df=time_df.xs(_type[a - 1], level='Type').reset_index('Level', drop=False)
    df['Level']=df['Level'].map(lambda _x:int(_x[b]))
    df_level=df['Level'].unique()
    df.set_index(['Level'],append=True,inplace=True)
    time_level_plot(df, df_level, None, ax13, 2,time_ratio,_color)
    ax13.set_frame_on(False)
    fig.suptitle(title + ": " + _Title, fontsize=20, y=0.92)

    x1=0.125
    x2=0.9
    y1=0.361
    _t=pd.Series([0,0,0,0,0,0])
    level_length=_t.T.add(level_length,fill_value=0.0,axis=0)
    h_cell=(y1-y2)/(len(it[str(study_columns[0])]) - 3)
    _h_cell=h_cell*(level_length.loc[0])
    y2=y1-_h_cell+0.001*2
    x=[(x1,x2),(x2,x1),(x1,x1)]
    y=[(y1,y1),(y2,y2),(y2,y1)]
    line1 = lines.Line2D(x,y,transform=fig.transFigure,c=colors[0],linewidth=2)
    y1=y2-0.001*2
    _h_cell=h_cell*(level_length.loc[1])
    y2=y1-_h_cell+0.001*2
    x=[(x1,x2),(x2,x1),(x1,x1)]
    y=[(y1,y1),(y2,y2),(y2,y1)]
    line2 = lines.Line2D(x,y,transform=fig.transFigure,c=colors[1],linewidth=2)
    y1=y2-0.001*2
    _h_cell=h_cell*(level_length.loc[2])
    y2=y1-_h_cell+0.001*2
    x=[(x1,x2),(x2,x1),(x1,x1)]
    y=[(y1,y1),(y2,y2),(y2,y1)]
    line3 = lines.Line2D(x,y,transform=fig.transFigure,c=colors[2],linewidth=2)
    y1=y2-0.001*2
    _h_cell=h_cell*(level_length.loc[3])
    y2=y1-_h_cell+0.001*2
    x=[(x1,x2),(x2,x1),(x1,x1)]
    y=[(y1,y1),(y2,y2),(y2,y1)]
    line4 = lines.Line2D(x,y,transform=fig.transFigure,c=colors[3],linewidth=2)
    y1=y2-0.001*2
    _h_cell=h_cell*(level_length.loc[4])
    y2=y1-_h_cell+0.001*1
    x=[(x1,x2),(x2,x1),(x1,x1)]
    y=[(y1,y1),(y2,y2),(y2,y1)]
    line5 = lines.Line2D(x,y,transform=fig.transFigure,c=colors[4],linewidth=2)
    y1=y2-0.0015*1
    _h_cell=h_cell*(level_length.loc[5])
    y2=y1-_h_cell+0.0015*0
    x=[(x1,x2),(x2,x1),(x1,x1)]
    y=[(y1,y1),(y2,y2),(y2,y1)]
    line6 = lines.Line2D(x,y,transform=fig.transFigure,c=colors[5],linewidth=2)
    if level_length.loc[5]<0.5:line6.set_linewidth(0)
    fig.lines = line1,line2,line3,line4,line5,line6
    if level_length.loc[0]<0.5:line1.set_linewidth(0)
    fig.lines = line1,line2,line3,line4,line5,line6
    ax2.set_frame_on(False)
    ax2.set_xlabel(None)
    ax2.tick_params(axis='y',tickdir='in')
    ax2.tick_params(axis='x',tickdir='out')
    ax5.tick_params(axis='x',tickdir='out',top=True)
    ax2.set_ylabel(None)
    ax2.set_xticklabels("")
    ax6.set_ylabel(None)
    ax12.set_frame_on(False)
    ax12.set_ylabel(None)
    ax12.set_xlabel(None)
    return 1