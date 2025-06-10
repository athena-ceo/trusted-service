package smartgov.rest;

public class MyResponse {

    public String name;
    public boolean eligible;

    public MyResponse() {
    }

    public MyResponse(String name, boolean eligible) {
        this.name = name;
        this.eligible = eligible;
    }
}