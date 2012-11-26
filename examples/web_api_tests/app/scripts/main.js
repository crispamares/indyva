console.log('* main running');
scinfo.connectServer()
    .then(console.log, console.log)
    .then(function () {
	    scinfo.dataStore.loadData('distances');
	  }
	 );

function main() {
    
}