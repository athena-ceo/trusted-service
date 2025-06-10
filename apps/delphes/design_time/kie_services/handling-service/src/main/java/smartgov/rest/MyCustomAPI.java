
package smartgov.rest;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

@Path("trusted-service/decide")
public class MyCustomAPI {

    @POST
    public MyResponse decide(MyRequest request) {
        return new MyResponse(request.name, 
                                request.name.length()<6);
    }
}