package smartgov.rest;

public class MyRequest {

    public String name;
    public String description;

    public MyRequest() {
    }

    public MyRequest(String name, String description) {
        this.name = name;
        this.description = description;
    }
}