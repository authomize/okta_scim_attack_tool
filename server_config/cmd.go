package api

import (
        "fmt"
        "github.com/julienschmidt/httprouter"
        "github.com/urfave/cli/v2"
        "net/http"
)

// Command returns a cli.Command that starts an HTTP router to serve the SCIM API.
func Command() *cli.Command {
        args := newArgs()
        return &cli.Command{
                Name:        "api",
                Description: "Manage state of resources defined in the SCIM (Simple Cloud Identity Management) protocol",
                Flags:       args.Flags(),
                Action: func(_ *cli.Context) error {
                        app := args.Initialize()
                        defer app.Close()

                        app.ensureSchemaRegistered()
                        basePath := args.Scim.BaseUrlPath

                        var router = httprouter.New()
                        {
                                router.GET(basePath + "/ServiceProviderConfig", ServiceProviderConfigHandler(app.ServiceProviderConfig()))
                                router.GET(basePath + "/Schemas", SchemasHandler())
                                router.GET(basePath + "/Schemas/:id", SchemaByIdHandler())
                                router.GET(basePath + "/ResourceTypes", ResourceTypesHandler(app.UserResourceType(), app.GroupResourceType()))
                                router.GET(basePath + "/ResourceTypes/:id", ResourceTypeByIdHandler(app.userResourceType, app.GroupResourceType()))

                                router.GET(basePath + "/Users/:id", GetHandler(app.UserGetService(), app.Logger()))
                                router.GET(basePath + "/Users", SearchHandler(app.UserQueryService(), app.Logger()))
                                router.POST(basePath + "/Users", CreateHandler(app.UserCreateService(), app.Logger()))
                                router.PUT(basePath + "/Users/:id", ReplaceHandler(app.UserReplaceService(), app.Logger()))
                                router.PATCH(basePath + "/Users/:id", PatchHandler(app.UserPatchService(), app.Logger()))
                                router.DELETE(basePath + "/Users/:id", DeleteHandler(app.UserDeleteService(), app.Logger()))

                                router.GET(basePath + "/Groups/:id", GetHandler(app.GroupGetService(), app.Logger()))
                                router.GET(basePath + "/Groups", SearchHandler(app.GroupQueryService(), app.Logger()))
                                router.POST(basePath + "/Groups", CreateHandler(app.GroupCreateService(), app.Logger()))
                                router.PUT(basePath + "/Groups/:id", ReplaceHandler(app.GroupReplaceService(), app.Logger()))
                                router.PATCH(basePath + "/Groups/:id", PatchHandler(app.GroupPatchService(), app.Logger()))
                                router.DELETE(basePath + "/Groups/:id", DeleteHandler(app.GroupDeleteService(), app.Logger()))

                                router.GET(basePath + "/health", HealthHandler(app.MongoClient(), app.RabbitMQConnection()))
                        }

                                //router.NotFound = router.GET(basePath + "/Users", SearchHandler(app.UserQueryService(), app.Logger()))

/*http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        app.Logger().Info().Fields(map[string]interface{}{
                "url": r.URL,
        }).Msg("URL not found")
        w.WriteHeader(http.StatusOK)
})*/

                        app.Logger().Info().Fields(map[string]interface{}{
                                "port": args.httpPort,
                        }).Msg("Listening for incoming requests. basePath = " + basePath)

                        return http.ListenAndServe(fmt.Sprintf(":%d", args.httpPort), router)
                },
        }
}
