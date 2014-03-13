/**
 * Created by Alastair on 09/03/2014.
 */
function changeLink() {
	var link = document.getElementById("mylink");
	
	window.open(link.href, '_blank');
	
	link.innerHTML = "Link";
	link.setAttribute('href', "PageC.html");
	//link.href = "PageC.html"; //does the same as above
	
	
	/*  $(link).click(function() {
		if(link.href = "PageB.html")
		{
			alert("hi PageC");
			link.setAttribute('href', "PageC.html");
		}
		else if(link.href = "PageC.html")
		{
			alert("hi PageB");
			link.setAttribute('href', "PageB.html");
		}
	});   */
	
	// latest
	/* switch(link.href)
	{
		case "PageB.html":
			alert("hiPageC");
			link.setAttribute('href', "PageC.html");
			return false;
		case "PageC.html":
			alert("hi");
			link.setAttribute('href', "PageB.html");
			return false;
	} */
	
	 /* if(link.href = "PageB.html")
		{
			alert("hiPageC");
			link.setAttribute('href', "PageC.html");
			return false;
		}
	
	else if(link.href = "PageC.html")
		{
			alert("hi");
			link.setAttribute('href', "PageB.html");
			return false;
		}  
	 */
	//return false;
}