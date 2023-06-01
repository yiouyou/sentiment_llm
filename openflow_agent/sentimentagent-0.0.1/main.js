// @ts-check
const { openiap } = require("@openiap/nodeapi");
/** 
 * @param {openiap} client
 * **/
async function onConnected(client) {
    var localqueue = await client.RegisterQueue({ queuename:""}, async (msg, payload, user, jwt)=> {
        var wi = await client.PopWorkitem({"wiq": "testq"});
        if(wi == null) {
            console.log("No workitem found");
            return;
        }
        // simulate work
        await new Promise(resolve => { setTimeout(resolve, 5000) });
        wi.state = "successful";
        await client.UpdateWorkitem({workitem: wi});
        console.log("Updated workitem");
    })
    console.log("listening on " + localqueue);
    var result = await client.Query({query: {}, projection: {"_created":1, "name":1}, top:5})
    console.log(JSON.stringify(result, null, 2))
}
async function main() {
    var client = new openiap();
    client.onConnected = onConnected
    await client.connect();
}
main();