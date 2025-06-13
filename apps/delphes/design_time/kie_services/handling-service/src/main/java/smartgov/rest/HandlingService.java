
package smartgov.rest;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import smartgov.rest.model.MyRequest;
import smartgov.rest.model.MyResponse;

import java.util.HashMap;

import org.kie.api.KieServices;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieRuntimeFactory;
import org.kie.dmn.api.core.DMNContext;
import org.kie.dmn.api.core.DMNDecisionResult;
import org.kie.dmn.api.core.DMNModel;
import org.kie.dmn.api.core.DMNResult;
import org.kie.dmn.api.core.DMNRuntime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Path("determine-handling")
public class HandlingService {


    private static final Logger logger = LoggerFactory.getLogger(HandlingService.class);

    @POST
    public MyResponse decide(MyRequest request) {

        KieServices kieServices = KieServices.Factory.get();
        KieContainer kieContainer = kieServices.getKieClasspathContainer();

        logger.info("-----> Creating a DMN runtime");

        DMNRuntime dmnRuntime = KieRuntimeFactory.of(kieContainer.getKieBase()).get(DMNRuntime.class);

        // TODO: see https://kie.apache.org/docs/10.0.x/drools/drools/KIE/index.html to configure a KieBase
        // TODO: read this to embed DMN models into a custom application
        // https://kie.apache.org/docs/10.0.x/drools/drools/DMN/index.html#dmn-execution-embedded-proc

        logger.info("-----> Getting a DMN model");
        String namespace = "https://kie.org/dmn/_DFB4B6B0-4D88-417C-9F48-7776A6266EA0";        


        // Model selection logic
        DMNModel modelNational = dmnRuntime.getModel(namespace, "HandlingNational");
        MyResponse nationalResponse = getResponse(dmnRuntime, modelNational, request);

        if ("78".equals(request.getCustomerData().getDepartement())) {
            DMNModel model78 = dmnRuntime.getModel(namespace, "Handling78");
            MyResponse response78 = getResponse(dmnRuntime, model78, request);

            return mergeResponse(response78, nationalResponse);
        }
        else 
            return nationalResponse;
    }

    MyResponse mergeResponse(MyResponse specificResp, MyResponse defaultResp) {
        return new MyResponse(specificResp.priority == null ? defaultResp.priority : specificResp.priority, 
                            specificResp.work_basket == null ? defaultResp.work_basket : specificResp.work_basket, 
                            specificResp.response_template_id == null ? defaultResp.response_template_id : specificResp.response_template_id, 
                            specificResp.acknowledgement_message == null ? defaultResp.acknowledgement_message : specificResp.acknowledgement_message, 
                            specificResp.handling == null ? defaultResp.handling : specificResp.handling);
    }

    MyResponse getResponse(DMNRuntime dmnRuntime, DMNModel dmnModel, MyRequest request) {
        logger.info("--------------");
        logger.info("-----> Creating input parameters for " + dmnModel.getName());
        DMNContext dmnContext = dmnRuntime.newContext();  
        dmnContext.set("the request", request);                 // TODO: does not work as expected...


        logger.info("-----> Executing DMN model");
        DMNResult dmnResult = dmnRuntime.evaluateAll(dmnModel, dmnContext);  

        logger.info("-----> Retrieving the result");
        
        String priority = null;
        String work_basket = null;
        String response_template_id = null;
        String acknowledgement_message = null;
        String handling = null;
        for (DMNDecisionResult dr : dmnResult.getDecisionResults()) {  
            logger.info(
                "Decision: " + dr.getDecisionName() + " = " + dr.getResult());       
            if (dr.getDecisionName().equals("Priority"))
                priority =  (String)dr.getResult();
            if (dr.getDecisionName().equals("WorkBasket"))
                work_basket =  (String)dr.getResult();
            if (dr.getDecisionName().equals("AckMessage"))
                acknowledgement_message =  (String)dr.getResult();
            if (dr.getDecisionName().equals("EmailTemplate"))
                response_template_id =  (String)dr.getResult();
            if (dr.getDecisionName().equals("Handling"))
                handling =  (String)dr.getResult();
         }

        logger.info("-----> Building response object for " + dmnModel.getName());
        // TODO: build a response from the DMNDecisionResult 
        return new MyResponse(priority, 
                                work_basket, 
                                response_template_id, 
                                acknowledgement_message, 
                                handling);
    }

}