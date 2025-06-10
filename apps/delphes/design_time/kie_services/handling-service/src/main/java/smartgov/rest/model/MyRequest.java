package smartgov.rest.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class MyRequest {

    private String intention;
    private CustomerCase customer_data;

    @JsonProperty("intention")
    @org.kie.dmn.feel.lang.FEELProperty("intention")
    public String getIntention() { return this.intention; }

    public void setIntention(String intention) { this.intention = intention; }

    @JsonProperty("customer_data")
    @org.kie.dmn.feel.lang.FEELProperty("customer_data")
    public CustomerCase getCustomerData() { return this.customer_data; }
    public void setCustomerData(CustomerCase customer_data) { this.customer_data = customer_data; }

    public MyRequest() {
    }

    public MyRequest(String intention, CustomerCase customer_data) {
        this.intention = intention;
        this.customer_data = customer_data;
    }
}