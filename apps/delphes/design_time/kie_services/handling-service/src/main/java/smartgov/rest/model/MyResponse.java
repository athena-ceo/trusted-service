package smartgov.rest.model;

public class MyResponse {

    public String priority;
    public String work_basket;
    public String response_template_id;
    public String acknowledgement_message;
    public String handling;

    public MyResponse() {
    }

    public MyResponse(String priority, String work_basket, String response_template_id, String acknowledgement_message, String handling) {
        this.priority = priority;
        this.work_basket = work_basket;
        this.response_template_id = response_template_id;
        this.acknowledgement_message = acknowledgement_message;
        this.handling = handling;

    }
}