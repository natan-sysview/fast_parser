package com.sysmining.test;
import java.util.List;
import java.util.ArrayList;

public class HelloWorld {
    private String nombre;
    private int version = 20;

    public HelloWorld(String nombre) {
        this.nombre = nombre;
    }

    public List<String> getProgramas(String sistema) {
        List<String> result = new ArrayList<>();
        if (sistema != null && !sistema.isEmpty()) {
            result.add("PRG001");
            result.add("PRG002");
        }
        return result;
    }
}
