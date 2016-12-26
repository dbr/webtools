/*global React */
/*global moment */
/*global $ */
/*global Mousetrap */
/*eslint no-console: ["error", { allow: ["warn", "error", "log"] }] */

function _do_video_action(video_id, name, force){
    if(typeof(force) === "undefined"){
        force=false;
    }

    console.log("Doing action", name, "for id", video_id, "forcefully", force);

    // Call grab method of API
    $.get("/youtube/api/1/video/" + video_id + "/" + name + "?force=" + force)
        .success(function(data){
            console.log("Initatised grab", data);
            data.status;
        }).error(function(data){
            console.log("Error initating grab", data);
            if(data.error){
                // TODO: Less annoying popup, allow force download
                if(confirm(data.error + "\n" + "Forcefully try again?")){
                    _do_video_action(video_id, name, true); // force
                }
            }
        });
}


var TimeAgo = React.createClass({
    render: function() {
        return <span title={this.props.time}>{moment(this.props.time).fromNow()}</span>;
    },
    tick: function(){
        this.forceUpdate();
    },
    componentDidMount: function() {
        this.timer = setInterval(this.tick, 1000);
    },
    componentWillUnmount: function(){
        clearInterval(this.timer);
    },
});


var VideoActions = React.createClass({
    download: function(e){
        e.preventDefault();
        console.log("Download " + this.props.videoid);
        _do_video_action(this.props.videoid, "grab");
    },
    ignore: function(e){
        e.preventDefault();
        _do_video_action(this.props.videoid, "mark_ignored");
    },
    render: function(){
        return (<span>
                <a href="#" onClick={this.download} title="Download video"><i className="fa fa-download" style={{color: "black"}}></i></a>
                &nbsp;
                <a href="#" onClick={this.ignore} title="Mark video as ignored"><i className="fa fa-square-o" style={{color: "black"}}></i></a>
                </span>);
    },
});

var VideoInfo = React.createClass({
    getInitialState: function(){
        return {};
    },
    humanName: function(status){
        return {
            NE: "new",
            GR: "grabbed",
            QU: "queued",
            DL: "downloading",
            GE: "grab error",
            IG: "ignored",
        }[status] || status;
    },
    cssClass: function(status){
        return {
            NE: "new",
            GR: "grabbed",
            QU: "queued",
            DL: "downloading",
            GE: "error",
            IG: "ignored",
        }[status] || status;
    },
    render: function(){
        return (
            <tr className={this.cssClass(this.props.data.status)}>
                <td><VideoActions videoid={this.props.data.id} video={this} /></td>
                <td>
                  <img width="16" height="16" src={this.props.data.channel.icon} />
                  &nbsp;
                  <a href={this.props.data.url}>{this.props.data.title}</a>
                  &nbsp;
                  <small>
                    <a href={"#/channels/"+this.props.data.channel.id} style={{color: "grey"}}>
                      [{this.props.data.channel.title}]
                    </a>
                  </small>
                </td>
                <td>
                  {this.humanName(this.props.data.status)}
                </td>
                <td>
                  <TimeAgo time={this.props.data.publishdate} />
                </td>
            </tr>
        );
    }
});

var SearchBox = React.createClass({
    filterstatus_parse: function(blah){
        var key_to_name = {
            NE: "new",
            GR: "grabbed",
            QU: "queued",
            DL: "downloading",
            GE: "grab error",
            IG: "ignored",
        };

        var statuses = {};
        key_to_name.forEach(function(v, k){
            status[k] = false;
        });

        var chunks = blah.split(",");
        chunks.forEach(function(x){
            if(x.length > 0 && x in statuses){
                statuses[x] = true;
            }
        });
        return statuses;
    },

    filterstatus_format: function(blah){
        var thing = [];
        blah.forEach(function(v, k){
            if(v){
                thing.push(k);
            }
        });
        return thing.join(",");
    },

    render: function(){
        return <div>
            <input onChange={this.changed} />
            Status:
            <input type="checkbox" id="status_new" name="status[new]" />
            <label            htmlFor="status_new">New</label>
            <input type="checkbox" id="status_grabbed" />
            <label            htmlFor="status_grabbed">Grabbed</label>
        </div>;
    },

    changed: function(event){
        this.props.cbFilterChange({
            text: event.target.value,
            status: this.filterstatus_format(this.status)});
    },
});

var NavigationLinks = React.createClass({
    getInitialState: function() {
        return {
            page: 1
        };
    },
    componentDidMount: function() {
        var that=this;
        Mousetrap.bind("n", function() { that.next(); });
        Mousetrap.bind("p", function() { that.prev(); });
    },
    setPage: function(pagenum){
        pagenum = Math.max(1, pagenum); // Clamp to positive
        console.log("Naviging to page " + pagenum);
        this.setState({page: pagenum});
        if(this.props.cbPageChanged){
            this.props.cbPageChanged(pagenum);
        }
    },
    render: function(){
        if(!this.props.data){
            return <div>Loading</div>;
        }

        var style_next = this.props.data.has_next ? {} : {pointerEvents: "none", color: "grey"};
        var style_back = this.props.data.has_previous ? {} : {pointerEvents: "none", color: "grey"};

        return (
            <div>
                Page {this.props.data.current} of {this.props.data && this.props.data.total}<br />
                <a style={style_back} href="#" onClick={this.prev}>Back</a> <a style={style_next} href="#" onClick={this.next}>Next</a>
            </div>
            );
    },
    prev: function(e){
        console.log("Previous!");
        this.setPage(this.state.page-1);
        if(e){
            e.preventDefault();
        }
    },
    next: function(e){
        console.log("Next!");
        this.setPage(this.state.page+1);
        if(e){
            e.preventDefault();
        }
    },
});

var VideoList = React.createClass({
    getInitialState: function(){
        return {data: {videos: []},
               filter: ""};
    },
    componentDidMount: function(){
        this.loadPage(1);
        this.timer = setInterval(this.tick, 1000);
    },

    componentWillUnmount: function() {
        clearInterval(this.timer);
    },

    tick: function(){
        // Collect up IDs for videos visible on current page
        var ids = [];
        this.state.data.videos.forEach(function(v){
            ids.push(v.id);
        });

        var self = this;

        // Query statues
        var status_query = $.ajax(
            {url:"/youtube/api/1/video_status?ids=" + ids.join(),
             dataType: "json"}
        );

        status_query.error(function(data){
            console.log("Error querying status");
        });

        status_query.success(function(data){
            // TODO: Make this simpler/tidier
            var newvideos = self.state.data.videos.map(function(v, index){

                if(data[v.id]){
                    return React.addons.update(v, {status: {$set: data[v.id]}});
                }
            });
            var newdata = React.addons.update(self.state.data, {videos: {$set: newvideos}});
            self.setState({data: newdata});
            /*
              self.state.data.videos.forEach(function(v, index){
              if(data[v.id]){
              self.state.data.videos[index].status = data[v.id];
              }
              });
            */
        });
    },

    loadPage: function(pagenum){
        $.ajax({
            url: "/youtube/api/1/channels/"+this.props.channel+"?page="+pagenum + "&search=" + this.state.filter,
            dataType: "json",
            success: function(data) {
                console.log("Got data!", data);
                this.setState({data: data});
            }.bind(this),
            error: function(xhr, textStatus){
                console.error("Error loading page (" + textStatus + ")");
            }
        });
    },
    setFilter: function(info){
        this.setState({filter: info.text});
        console.log("Filter status", info);
        this.loadPage(0);
    },

    render: function(){
        var items = this.state.data.videos.map(function(f){
            return (<VideoInfo key={f.id} data={f} />);
        });

        return (
            <div>
                <NavigationLinks data={this.state.data.pagination} cbPageChanged={this.loadPage}/>
                <SearchBox cbFilterChange={this.setFilter}/>

                <table>
                  <thead>
                    <th width="42px"></th>
                    <th>              Title</th>
                    <th width="75px"> Status</th>
                    <th width="160px">Released</th>
                  </thead>
                  {items}
                </table>

                <NavigationLinks data={this.state.data.pagination} cbPageChanged={this.loadPage}/>
            </div>
            );
    }
});


var ChannelList = React.createClass({
    getInitialState: function(){
        return {data: {channels: []},
                is_loaded: false};
    },
    componentDidMount: function(){
        this.load();
    },
    load: function(){
        $.ajax({
            url: "/youtube/api/1/channels",
            dataType: "json",
            success: function(data) {
                console.log("Got data!", data);
                if(this.isMounted()){
                    this.setState({data: data, is_loaded: true});
                }
            }.bind(this),
            error: function(xhr, textStatus){
                console.error("Error loading page (" + textStatus + ")");
            }.bind(this)
        });
    },

    render: function(){
        if(!this.state.is_loaded){
            return(<div>Loading!</div>);
        }
        var things = this.state.data.channels.map(function(f){
            return (<tr key={f.id}>
                      <td>
                        <img src={f.icon} width="16" height="16" /> <a href={"#/channels/"+f.id}>{f.title || "Untitled channel (refreshing?)"}</a>
                      </td>
                      <td>
                      </td>
                    </tr>);
        });
        return (
            <div>
              <table>
                <tr>
                <td><a href="#/channels/_all">All channels</a></td>
                </tr>
                {things}
              </table>
              <h2>Download list</h2>
              <DownloadList />
            </div>
        );
    },
});

var ChannelAdd = React.createClass({
    getInitialState: function(){
        return {channame: "", service: "youtube"};
    },
    handleChangeID: function(event){
        this.setState({chanid: event.target.value});
    },

    handleChangeService: function(event){
        this.setState({service: event.target.value});
    },

    submit: function(event){
        console.log("Go");
        var thing = $.ajax({
            url: "/youtube/api/1/channel_add",
            type: "POST",
            data: {"service": this.state.service,
                   "chanid": this.state.chanid}});
        thing.error(function(data){
            console.log("Error adding channel!");
            alert("Error adding channel! Check Developer Console for more information");
            // TODO: Better error message
        });
        thing.success(function(data){
            alert("Done!");
            // TODO: Redirect to new channel
        });
    },

    render: function(){
        return (<form onSubmit={this.submit}>
                  <input value={this.state.chanid} type="text" onChange={this.handleChangeID} />
                  <select value={this.state.service} onChange={this.handleChangeService}>
                    <option value="youtube">YouTube</option>
                    <option value="vimeo">Vimeo</option>
                  </select>
                  <input type="submit" />
                </form>);
    },
});

var DownloadList = React.createClass({
    getInitialState: function(){
        return {active: []};
    },
    componentDidMount: function(){
        this.refresh();
        this.timer = setInterval(this.refresh, 500);
    },
    componentWillUnmount: function() {
        clearInterval(this.timer);
    },
    refresh: function(){
        var that = this;

        var thing = $.ajax({
            url: "/youtube/api/1/downloads",
            type: "GET",
            dataType: "json",
        });

        thing.success(function(data){
            if(that.componentIsMounted){
                that.setState({active: data});
            }
        });
    },
    render: function(){
        var items = [];
        for (var property in this.state.active) {
            if (this.state.active.hasOwnProperty(property)) {
                var cur = this.state.active[property];

                items.push(
                    <tr key={cur.id}>
                        <td>
                        {cur.title}
                        </td>
                        <td>
                        {cur.status}
                        </td>
                    <td>
                        {cur.message}
                    </td>
                    </tr>
                );
            }
        }

        return (
            <table width="600">
              {items}
            </table>
        );
    },
});

var PageNotFound = React.createClass({
    render: function(){
        return (
            <span>Unknown page</span>
        );
    },
});

var App = React.createClass({
    getInitialState: function(){
        return {component: <div />};
    },
    componentDidMount: function(){
        var self=this;

        var routes = {
            "/": function(){ self.setState({component: <ChannelList />}); },
            "/channels/:id": function(chanid){ self.setState({component: <VideoList key={chanid} channel={chanid} />}); },
            "/add": function(){ self.setState({component: <ChannelAdd />}); },
        };

        var router = Router(routes);
        router.init("/");
    },
    render: function(){
        console.log("App rendering", this.state.component);
        return <div>
            <p><a href="#/">Channel list</a> | <a href="#/add">Add channel</a> | <a href="/youtube/api/1/refresh?channel=_all">Refresh all</a></p>
            {this.state.component}
        </div>;
    },
});

React.render(<App />, document.getElementById("content"));
